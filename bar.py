# import the necessary packages
from pyzbar import pyzbar
import cv2
# load the input image
class QR:
	code = 'unknown'
	user = ''
	name ='unknown'
	def menu(self):
		"""
        Input method allows engineer who doesn't have usb camera to
		get the corresponding QR code and call the decode method
        """
		while True:
			code = input ("please select your QRcode: ")
			QR.user='/Users/ltm/Desktop/QR_code/dataset/{}.png'.format(code)
			break
		self.decode()
	def decode(self):
		"""
        decode method find the QR code in the dataset decode it from image to strint
        :return: return the username
        """
		image = cv2.imread(QR.user)
		# find the barcodes in the image and decode each of the barcodes
		try:
			barcodes = pyzbar.decode(image)
			# loop over the detected barcodes
			for barcode in barcodes:
				# extract the bounding box location of the barcode and draw the
				# bounding box surrounding the barcode on the image
				(x, y, w, h) = barcode.rect
				cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
				# the barcode data is a bytes object so if we want to draw it on
				# our output image we need to convert it to a string first
				barcodeData = barcode.data.decode("utf-8")
				barcodeType = barcode.type
				# draw the barcode data and barcode type on the image
				text = "{} ({})".format(barcodeData, barcodeType)
				cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
					0.5, (0, 0, 255), 2)
				# print the barcode type and data to the terminal
				print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
				QR.name = barcodeData
			# show the output image
			cv2.imshow("Image", image)
			cv2.waitKey(0)
		except TypeError as e:
			print("Can't find your QRcode in the dataset")

	def get_info(self):
		return QR.name
	def run(self):
		"""
        Call the the menu method 
        """
		self.menu()
        
if __name__ == '__main__':
    QR().run()
