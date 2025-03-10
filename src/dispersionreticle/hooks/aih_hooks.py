import logging

import BigWorld
import AvatarInputHandler
from AvatarInputHandler import gun_marker_ctrl
from constants import ARENA_PERIOD

from dispersionreticle.utils import *
from dispersionreticle.utils import debug_state
from dispersionreticle.utils.reticle_registry import ReticleRegistry


logger = logging.getLogger(__name__)

if debug_state.IS_DEBUGGING:
    logger.setLevel(logging.DEBUG)


###########################################################
# AvatarInputHandler hooks
# Needed to invoke update method on gun markers of new markerType
#
# Basically, AvatarInputHandler invokes updateGunMarker
# method on currently selected control mode (control_modes.py)
# which then invokes update on gun marker decorator (gun_marker_ctrl.py)
# that manages individual markers.
#
# Without this override, client and server focus gun markers
# wouldn't be updated.
#
# Notes:
# - Every control mode related to gun markers (there are few of them) has their own gun marker decorator.
###########################################################


@overrideIn(AvatarInputHandler.AvatarInputHandler)
def updateClientGunMarker(func, self, pos, direction, size, relaxTime, collData):
    func(self, pos, direction, size, relaxTime, collData)

    for reticle in ReticleRegistry.RETICLES:
        if not reticle.isServerReticle():
            self._AvatarInputHandler__curCtrl.updateGunMarker(reticle.gunMarkerType,
                                                              pos, direction, size, relaxTime, collData)


@overrideIn(AvatarInputHandler.AvatarInputHandler)
def updateServerGunMarker(func, self, pos, direction, size, relaxTime, collData):
    func(self, pos, direction, size, relaxTime, collData)

    for reticle in ReticleRegistry.RETICLES:
        if reticle.isServerReticle():
            self._AvatarInputHandler__curCtrl.updateGunMarker(reticle.gunMarkerType,
                                                              pos, direction, size, relaxTime, collData)


# I think we don't have to bother with DUAL_ACC overrides yet
# I don't even know how it will be used


@overrideIn(AvatarInputHandler.AvatarInputHandler, clientType=ClientType.WG)
def __onArenaStarted(func, self, period, *args):
    common_onArenaStarted(func, self, period, *args)


# Lesta specific
# changed method name
@overrideIn(AvatarInputHandler.AvatarInputHandler, clientType=ClientType.LESTA)
def _onArenaStarted(func, self, period, *args):
    common_onArenaStarted(func, self, period, *args)


def common_onArenaStarted(func, self, period, *args):
    func(self, period, *args)

    # this event handler is called multiple times
    # we only want to react to it when battle start finishes countdown
    if period != ARENA_PERIOD.BATTLE:
        return

    # TODO fix it in a more sophisticated way than "this"
    #
    # in Onslaught game mode something weird happens to server gun markers
    # when selecting different than initial vehicle before countdown finishes
    #
    # by this code, we will invalidate BigWorld internal state to reboot GunMarkerComponent
    # as soon as the game starts
    #
    # generally I want to analyze server marker state more precisely with DebugStateCollector
    # however, when I got some free time, Onslaught event has already finished
    # so I cannot find real root cause now
    #
    # previously I've fixed it with blind guess quickly restarting showServerMarker flag and it worked
    # but rebooting is not the finest way to workaround bugs
    #
    # not only that, but after first version of this fix was implemented, it fixed
    # upper mentioned DETERMINISTIC bug in Onslaught
    # HOWEVER, new NON-DETERMINISTIC bug has appeared when certain conditions were met in ANY MATCH:
    # - user was using enabled "Use server aim" from in-game menu
    # - user were not using any server-related reticles from this mod config
    #
    # this bug happens quite rarely and randomly (around 5%-10% chance to appear), but often enough to bother users
    # after roughly 30 matches (I have bad luck as you see) I've managed to reproduce it
    # and introspect all server reticle related variables when it occurred
    # everything was fine with all of them
    # most importantly, Avatar#enableServerAim was eventually called with True when it needed to be True
    #
    # my guess is that
    # changing "server_marker" developer feature flag too fast may cause
    # some consecutive calls to be completely ignored, in result, we may end up with DISABLED server aim
    # despite calling it with True
    #
    # in other words, it looks like setting developer feature flags on Avatar base
    # may be NON-BLOCKING ASYNCHRONOUS operation (or something really is messed up that I haven't noticed yet)
    #
    # or it might be related to __onArenaStarted being called by BigWorld
    # and bug is some race condition that messes up "server_marker" flag
    #
    # either way, to workaround this, we will delay calls a little bit to be (most likely) sure BigWorld caught up
    # to accept consecutive call (probably 1 ms would be fine, but let's throw 40 ms to be sure, why the heck not)
    #
    # this is overall bad, but for now it is what it is

    logger.debug("Onslaught server marker fix start")

    def negateGunMarkerComponentState():
        logger.debug("Onslaught server marker fix negate begin")
        BigWorld.player().gunRotator.showServerMarker = not gun_marker_ctrl.useServerGunMarker()
        logger.debug("Onslaught server marker fix negate finished")

        # 2: schedule restore
        BigWorld.callback(0.04, restoreGunMarkerComponentState)

    def restoreGunMarkerComponentState():
        logger.debug("Onslaught server marker fix restore begin")
        BigWorld.player().gunRotator.showServerMarker = gun_marker_ctrl.useServerGunMarker()
        logger.debug("Onslaught server marker fix restore finished")

    # 1: schedule negation
    BigWorld.callback(0.04, negateGunMarkerComponentState)
