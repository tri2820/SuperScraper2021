
'''
# TODO: Make setup to extract pdf-pages as images
# TODO: Get that training data goin'
# TODO: Game-end my self making bbox setup
# TODO: Kill computer with obj detection
'''


from pdf_image_extraction import PdfImageExtractor

pdf_extractor = PdfImageExtractor()

pdf_extractor.extract_images()

images_path = 'images\pdf-page-images'
xml_path = 'images\labeled-all'

test_path = 'images\\test'
train_path = 'images\\train'


pdf_extractor.train_test_file_split(images_path, xml_path, train_path, test_path, 0.2)














































# --
