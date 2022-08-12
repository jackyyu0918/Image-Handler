from PIL import Image
import imagehash


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    hash0 = imagehash.average_hash(Image.open('dog_1.jpg'))
    hash1 = imagehash.average_hash(Image.open('dog_2.jpg'))
    cutoff = 5  # maximum bits that could be different between the hashes.

    if hash0 - hash1 < cutoff:
        print('images are similar')
    else:
        print('images are not similar')
