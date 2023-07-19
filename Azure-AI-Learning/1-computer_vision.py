from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import os

os.system("color")
class colors:
    green = '\033[92m'
    blue = '\033[94m'
    red = '\033[31m'
    yellow = '\033[33m'
    reset = '\033[0m'

cog_endpoint = os.environ.get('azurecognitiveservicesendpoint')
cog_key = os.environ.get('azurecognitiveserviceskey')


# Change the URL between the quotes below to run your own images!
image_to_analyze = "https://raw.githubusercontent.com/ACloudGuru/content-AI-900/main/images/image-analysis/1-computervision-couple.jpg"


computervision_client = ComputerVisionClient(cog_endpoint, CognitiveServicesCredentials(cog_key))

image_analysis = computervision_client.analyze_image(image_to_analyze,visual_features=[VisualFeatureTypes.description,
 VisualFeatureTypes.tags, VisualFeatureTypes.faces])

print("\n-----Image Description-----")
for caption in image_analysis.description.captions:
    print(f"{colors.green}Confidence: {colors.reset}" + str(caption.confidence))
    print(f"{colors.green}Description: {colors.reset}" + caption.text)
print("----------\n")


input("Press Enter to continue to image tags...\n")


print("-----Image Tags-----")
for tag in image_analysis.tags:
    print(f"{colors.green}Tag:{colors.reset} {tag.name:<15}", 
    f" {colors.yellow}Confidence:{colors.reset} {tag.confidence:<15}")
print("----------\n")


input("Press Enter to continue to face detection...\n")


print("-----Face Detection-----")
for face in image_analysis.faces:
    print("Face at location {},{},{},{}".format( face.face_rectangle.left, face.face_rectangle.top, \
        face.face_rectangle.left + face.face_rectangle.width, \
        face.face_rectangle.top + face.face_rectangle.height))
print("----------")

input("\nPress Enter to Exit...")
