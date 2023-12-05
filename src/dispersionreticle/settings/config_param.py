from dispersionreticle.settings.config_param_types import *
from dispersionreticle.settings.translations import Tr


class ConfigParams(object):

    def __init__(self):
        self.__tokenNameRegistry = {}

        self.enabled = BooleanParam(
            ["enabled"],
            defaultValue=True, disabledValue=False
        )
        self.dispersionReticleEnabled = BooleanParam(
            ["dispersion-reticle", "enabled"],
            defaultValue=True, disabledValue=False
        )

        self.latencyReticleEnabled = BooleanParam(
            ["latency-reticle", "enabled"],
            defaultValue=False
        )
        self.latencyReticleHideStandardReticle = BooleanParam(
            ["latency-reticle", "hide-standard-reticle"],
            defaultValue=False
        )

        self.serverReticleEnabled = BooleanParam(
            ["server-reticle", "enabled"],
            defaultValue=False
        )

        self.simpleServerReticleEnabled = BooleanParam(
            ["simple-server-reticle", "enabled"],
            defaultValue=False
        )
        self.simpleServerReticleShape = OptionsParam(
            ["simple-server-reticle", "shape"],
            [
                Option("pentagon", 0, "1. " + Tr.SIMPLE_SERVER_RETICLE_PART_SHAPE_OPTION_PENTAGON),
                Option("t-shape", 1, "2. " + Tr.SIMPLE_SERVER_RETICLE_PART_SHAPE_OPTION_T_SHAPE),
                Option("circle", 2, "3. " + Tr.SIMPLE_SERVER_RETICLE_PART_SHAPE_OPTION_CIRCLE),
                Option("dashed", 3, "4. " + Tr.SIMPLE_SERVER_RETICLE_PART_SHAPE_OPTION_DASHED)
            ],
            defaultValue="pentagon"
        )
        self.simpleServerReticleColor = ColorParam(
            ["simple-server-reticle", "color"],
            defaultValue=(255, 0, 255)
        )
        self.simpleServerReticleDrawCenterDot = BooleanParam(
            ["simple-server-reticle", "draw-center-dot"],
            defaultValue=False
        )
        self.simpleServerReticleDrawOutline = BooleanParam(
            ["simple-server-reticle", "draw-outline"],
            defaultValue=False
        )
        self.simpleServerReticleBlend = FloatSliderParam(
            ["simple-server-reticle", "blend"],
            minValue=0.0, step=0.01, maxValue=1.0,
            defaultValue=0.5
        )
        self.simpleServerReticleAlpha = FloatSliderParam(
            ["simple-server-reticle", "alpha"],
            minValue=0.0, step=0.01, maxValue=1.0,
            defaultValue=1.0
        )

        self.reticleSizeMultiplier = FloatTextParam(
            ["reticle-size-multiplier"],
            minValue=0.0, maxValue=None,
            defaultValue=1.0
        )

    def items(self):
        return PARAM_REGISTRY.items()


g_configParams = ConfigParams()
