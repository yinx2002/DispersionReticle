from aih_constants import GUN_MARKER_TYPE

from dispersionreticle.utils.reticle_types.vanilla_reticle import VanillaReticle


class AS3Reticle(VanillaReticle):

    def getFlashMarkerNames(self):
        return (
            self.arcadeGunMarkerName,
            self.sniperGunMarkerName,
            self.dualGunArcadeGunMarkerName,
            self.dualGunSniperGunMarkerName
        )

    # gm_factory
    def createDefaultMarkers(self, gunMarkerFactory, markerType):
        if markerType != GUN_MARKER_TYPE.UNDEFINED:
            return (gunMarkerFactory._createAS3ArcadeMarker(self.gunMarkerType, self.arcadeGunMarkerName),
                    gunMarkerFactory._createAS3SniperMarker(self.gunMarkerType, self.sniperGunMarkerName))
        return (gunMarkerFactory._createAS3ArcadeMarker(GUN_MARKER_TYPE.UNDEFINED, self.arcadeGunMarkerName),
                gunMarkerFactory._createAS3SniperMarker(GUN_MARKER_TYPE.UNDEFINED, self.sniperGunMarkerName))

    # gm_factory
    def createSPGMarkers(self, gunMarkerFactory, markerType):
        # important
        # here we avoid spawning AS3 marker for SPG
        # because it will simply "not work normally"
        if markerType != GUN_MARKER_TYPE.UNDEFINED:
            return (gunMarkerFactory._createAS3ArcadeMarker(self.gunMarkerType, self.arcadeGunMarkerName),
                    gunMarkerFactory._createSPGMarker(self.gunMarkerType, self.spgGunMarkerName))
        return (gunMarkerFactory._createAS3ArcadeMarker(GUN_MARKER_TYPE.UNDEFINED, self.arcadeGunMarkerName),
                gunMarkerFactory._createSPGMarker(GUN_MARKER_TYPE.UNDEFINED, self.spgGunMarkerName))

    # gm_factory
    def createArcadeOnlySPGMarkers(self, gunMarkerFactory, markerType):
        if markerType != GUN_MARKER_TYPE.UNDEFINED:
            return (gunMarkerFactory._createAS3ArcadeMarker(self.gunMarkerType, self.arcadeGunMarkerName),)
        return (gunMarkerFactory._createAS3ArcadeMarker(GUN_MARKER_TYPE.UNDEFINED, self.arcadeGunMarkerName),)

    # gm_factory
    def createDualGunMarkers(self, gunMarkerFactory, markerType):
        if markerType != GUN_MARKER_TYPE.UNDEFINED:
            return (gunMarkerFactory._createAS3ArcadeMarker(self.gunMarkerType, self.dualGunArcadeGunMarkerName),
                    gunMarkerFactory._createAS3SniperMarker(self.gunMarkerType, self.dualGunSniperGunMarkerName))
        return (gunMarkerFactory._createAS3ArcadeMarker(GUN_MARKER_TYPE.UNDEFINED, self.dualGunArcadeGunMarkerName),
                gunMarkerFactory._createAS3SniperMarker(GUN_MARKER_TYPE.UNDEFINED, self.dualGunSniperGunMarkerName))
