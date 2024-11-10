from .comparison_view import ComparisonView


class GaussianFilterView(ComparisonView):
    def __init__(self, root, controller, original_image_cv, filtered_image_cv):
        super().__init__(root, controller, original_image_cv, filtered_image_cv, "Gaussian Filter")