import argparse
import random
import unishox2
from pprint import pprint

parser = argparse.ArgumentParser(
    description=(
        "Uses unishox2 to test compression and decompression of a given "
        "string. If no string is given, an example string is used."
    )
)
parser.add_argument("--string", action="store", type=str, help="Your test string!")
parser.add_argument(
    "--iterations", action="store", type=int, default=1, help="Iterations!"
)
args = parser.parse_args()

example_strings = [
    "Beauty is not in the face. Beauty is a light in the heart.",
    "La belleza no está en la cara. La belleza es una luz en el corazón.",
    "La beauté est pas dans le visage. La beauté est la lumière dans le coeur.",
    "A beleza não está na cara. A beleza é a luz no coração.",
    "Schoonheid is niet in het gezicht. Schoonheid is een licht in het hart.",
    "Schönheit ist nicht im Gesicht. Schönheit ist ein Licht im Herzen.",
    "La belleza no está en la cara. La belleza es una luz en el corazón.",
    "La beauté est pas dans le visage. La beauté est la lumière dans le coeur.",
    "La bellezza non è in faccia. La bellezza è la luce nel cuore.",
    "Skönhet är inte i ansiktet. Skönhet är ett ljus i hjärtat.",
    "Frumusețea nu este în față. Frumusețea este o lumină în inimă.",
    "Краса не в особі. Краса - це світло в серці.",
    "Η ομορφιά δεν είναι στο πρόσωπο. Η ομορφιά είναι ένα φως στην καρδιά.",
    "Güzellik yüzünde değil. Güzellik, kalbin içindeki bir ışıktır.",
    "Piękno nie jest na twarzy. Piękno jest światłem w sercu.",
    "Skoonheid is nie in die gesig nie. Skoonheid is 'n lig in die hart.",
    "Beauty si katika uso. Uzuri ni nuru moyoni.",
    "Ubuhle abukho ebusweni. Ubuhle bungukukhanya enhliziyweni.",
    "Beauty ma aha in wajiga. Beauty waa iftiin ah ee wadnaha.",
    "Красота не в лицо. Красота - это свет в сердце.",
    "الجمال ليس في الوجه. الجمال هو النور الذي في القلب.",
    "زیبایی در چهره نیست. زیبایی نور در قلب است.",
    "ښکلا په مخ کې نه ده. ښکلا په زړه کی یوه رڼا ده.",
    "Gözəllik üzdə deyil. Gözəllik qəlbdə bir işıqdır.",
    "Go'zallik yuzida emas. Go'zallik - qalbdagi nur.",
    "Bedewî ne di rû de ye. Bedewî di dil de ronahiyek e.",
    "خوبصورتی چہرے میں نہیں ہے۔ خوبصورتی دل میں روشنی ہے۔",
    "सुंदरता चेहरे में नहीं है। सौंदर्य हृदय में प्रकाश है।",
    "সৌন্দর্য মুখে নেই। সৌন্দর্য হৃদয় একটি আলো।",
    "ਸੁੰਦਰਤਾ ਚਿਹਰੇ ਵਿੱਚ ਨਹੀਂ ਹੈ. ਸੁੰਦਰਤਾ ਦੇ ਦਿਲ ਵਿਚ ਚਾਨਣ ਹੈ.",
    "అందం ముఖంలో లేదు. అందం హృదయంలో ఒక కాంతి.",
    "அழகு முகத்தில் இல்லை. அழகு என்பது இதயத்தின் ஒளி.",
    "सौंदर्य चेहरा नाही. सौंदर्य हे हृदयातील एक प्रकाश आहे.",
    "ಸೌಂದರ್ಯವು ಮುಖದ ಮೇಲೆ ಇಲ್ಲ. ಸೌಂದರ್ಯವು ಹೃದಯದಲ್ಲಿ ಒಂದು ಬೆಳಕು.",
    "સુંદરતા ચહેરા પર નથી. સુંદરતા હૃદયમાં પ્રકાશ છે.",
    "സൗന്ദര്യം മുഖത്ത് ഇല്ല. സൗന്ദര്യം ഹൃദയത്തിലെ ഒരു പ്രകാശമാണ്.",
    "सौन्दर्य अनुहारमा छैन। सौन्दर्य मुटुको उज्यालो हो।",
    "රූපලාවන්ය මුහුණේ නොවේ. රූපලාවන්ය හදවත තුළ ඇති ආලෝකය වේ.",
    "美是不是在脸上。 美是心中的亮光。",
    "Beauty ora ing pasuryan. Kaendahan iku cahya ing sajroning ati.",
    "美は顔にありません。美は心の中の光です。",
    "Ang kagandahan ay wala sa mukha. Ang kagandahan ay ang ilaw sa puso.",
    "아름다움은 얼굴에 없습니다。아름다움은 마음의 빛입니다。",
    "Vẻ đẹp không nằm trong khuôn mặt. Vẻ đẹp là ánh sáng trong tim.",
    "ความงามไม่ได้อยู่ที่ใบหน้า ความงามเป็นแสงสว่างในใจ",
    "အလှအပမျက်နှာပေါ်မှာမဟုတ်ပါဘူး။ အလှအပစိတ်နှလုံးထဲမှာအလင်းကိုဖြစ်ပါတယ်။",
    "Kecantikan bukan di muka. Kecantikan adalah cahaya di dalam hati.",
    "💃🚫😦,💃📥🎆❤️️",
]

if not args.string:
    args.string = random.choice(example_strings)

pprint(args.string)

for i in range(0, args.iterations):
    print("Compresses to ...")
    compressed, original_size = unishox2.compress(args.string)
    pprint(compressed)

    print("Decompresses to ...")
    decompressed = unishox2.decompress(compressed, original_size)
    pprint(decompressed)

    # The original length is only an optional hint - this also works
    assert unishox2.decompress(compressed) == args.string

    if args.string == decompressed:
        print("Test succeeded!")
        # As `compressed` is already raw bytes, we can also call len() on this ...
        compressed_size = len(compressed)
        ratio = compressed_size / original_size
        if ratio < 1:
            percent = round((1 - ratio) * 100, 2)
            print(
                f"Stored this string with {compressed_size}b/{original_size}b = {percent}% less space"
            )
        else:
            percent = round(abs(1 - ratio) * 100, 2)
            print(
                f"Stored this string with {compressed_size}b/{original_size}b = {percent}% more space :("
            )
    else:
        # heck
        print(
            "Test failed. Please leave an issue! https://github.com/tweedge/unishox2-py3/issues"
        )
