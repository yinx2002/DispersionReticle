import logging
from functools import wraps

from BWUtil import AsyncReturn
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import SimpleDialogMeta, I18nInfoDialogButtons
from realm import CURRENT_REALM
from wg_async import wg_async, _Promise, wg_await, BrokenPromiseError, delay

from dispersionreticle.settings.translations import Tr


logger = logging.getLogger(__name__)


class ClientType(object):
    WG = "EU"
    LESTA = "RU"


def overrideIn(cls, clientType=None, onlyWhenDebugging=False):
    from dispersionreticle.utils import debug_state

    def _overrideMethod(func):
        if onlyWhenDebugging and not debug_state.IS_DEBUGGING:
            return func

        if clientType is not None and clientType != CURRENT_REALM:
            return func

        funcName = func.__name__

        if funcName.startswith("__"):
            funcName = "_" + cls.__name__ + funcName

        old = getattr(cls, funcName)

        @wraps(old)
        def wrapper(*args, **kwargs):
            return func(old, *args, **kwargs)

        setattr(cls, funcName, wrapper)
        return wrapper
    return _overrideMethod


# Utility decorator to add new function in certain class/module
def addMethodTo(cls, onlyWhenDebugging=False):
    from dispersionreticle.utils import debug_state

    def _overrideMethod(func):
        if onlyWhenDebugging and not debug_state.IS_DEBUGGING:
            return func

        setattr(cls, func.__name__, func)
        return func
    return _overrideMethod


def getClientType():
    return CURRENT_REALM


def isClientWG():
    return CURRENT_REALM == ClientType.WG


def isClientLesta():
    return CURRENT_REALM == ClientType.LESTA


@wg_async
def displayDialog(message):
    while True:
        try:
            yield await_callback_param(DialogsInterface.showDialog, callbackParamName="callback")(
                SimpleDialogMeta(title=Tr.MODNAME,
                                 message=message,
                                 buttons=I18nInfoDialogButtons(i18nKey="common/error"))
            )
            break
        except BrokenPromiseError:
            # it may happen that, in whatever Page app we wanted to
            # display dialog window is not present, then _Promise associated
            # with our callback instantly goes out of scope (because our callback is not bound to anything)
            # and when that happens, python GC will "del _Promise"
            # effectively breaking this _Promise, resulting in this exception
            #
            # when that happens, wait until there is "something" we can display it to
            # I'd rather perform simple waiting than hooking into something when any app is initialized
            logger.warning("Cannot display dialog yet, try next second")
            yield wg_await(delay(1.0))
            continue
        except Exception:
            logger.warning("Failed to display warning dialog window.", exc_info=True)
            break


# wg_async
#
# Slightly modified version of await_callback function to have
# better control over parameter name being callback we're waiting to be called
def await_callback_param(func, timeout=None, callbackParamName="callback"):

    def wrapper(*args, **kwargs):
        promise = _Promise()

        def callback(*args):
            if len(args) == 1:
                args = args[0]
            promise.set_value(args)

        kwargs[callbackParamName] = callback
        func(*args, **kwargs)
        return wg_await(promise.get_future(), timeout)

    return wrapper


class ObservingSemaphore(object):

    def __init__(self):
        self.observerCount = 0

    def __enter__(self):
        self.observerCount += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.observerCount -= 1

    def __nonzero__(self):
        return self.observerCount > 0

    def withIgnoringLock(self, returnForIgnored):

        def _withIgnoringLock(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if self:
                    return returnForIgnored

                with self:
                    return func(*args, **kwargs)

            return wrapper

        return _withIgnoringLock

    def withAsyncIgnoringLock(self, returnForIgnored):

        def _withAsyncIgnoringLock(func):
            @wg_async
            @wraps(func)
            def wrapper(*args, **kwargs):
                if self:
                    raise AsyncReturn(returnForIgnored)

                with self:
                    result = yield wg_await(func(*args, **kwargs))
                    raise AsyncReturn(result)

            return wrapper

        return _withAsyncIgnoringLock
