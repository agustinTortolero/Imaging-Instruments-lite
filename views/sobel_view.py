from .comparison_view import ComparisonView


class SobelView(ComparisonView):
    def __init__(self, root, controller, original_image_cv, sobel_image_cv):
        super().__init__(root, controller, original_image_cv, sobel_image_cv, "Edges Detection")
        # Call show_images to ensure images are shown correctly
        #self.show_images()