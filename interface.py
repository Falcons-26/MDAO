from structural_surrogate.wing_surrogate import WingSurrogate
from structural_surrogate.fuse_surrogate import FuselageSurrogate

# ---- GLOBAL MODELS ----
wing_model = None
fuse_model = None


def initialize_structural_surrogates():
    """
    Must be called ONCE before MDO loop starts.
    """
    global wing_model, fuse_model

    print("\n--- Initializing structural surrogate ---")

    wing_model = WingSurrogate()
    wing_model.load_and_train()

    fuse_model = FuselageSurrogate()
    fuse_model.load_and_train()

    print("Structural surrogates ready.")


def get_structural_weight(
    wingspan,
    wing_chord,
    fuse_chord
):
    """
    Returns:
        total_structural_weight_g,
        wing_weight_g,
        fuselage_weight_g
    """
    if wing_model is None or fuse_model is None:
        raise RuntimeError(
            "Structural surrogates not initialized. "
            "Call initialize_structural_surrogates() first."
        )

    W_wing_g = wing_model.predict(wingspan, wing_chord)
    W_fuse_g = fuse_model.predict(fuse_chord)

    W_struct_g = W_wing_g + W_fuse_g

    return W_struct_g, W_wing_g, W_fuse_g
