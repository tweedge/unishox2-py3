import pytest
from hypothesis import given, settings
from hypothesis.strategies import integers, text

import unishox2


def test_ok():
    """
    Simple test case.
    """
    string = "The quick brown fox jumps over the lazy dog."
    compressed, original_size = unishox2.compress(string)
    decompressed = unishox2.decompress(compressed, original_size)
    assert decompressed == string


def test_compress_non_str():
    """
    Verify only strings are accepted by compress.
    """
    string = "The quick brown fox jumps over the lazy dog."
    with pytest.raises(TypeError):
        unishox2.compress([string])
    with pytest.raises(TypeError):
        unishox2.compress((string,))
    with pytest.raises(TypeError):
        unishox2.compress({"string": string})
    with pytest.raises(TypeError):
        unishox2.compress(1)
    with pytest.raises(TypeError):
        unishox2.compress(1.5)


def test_decompress_non_bytes():
    """
    Verify only bytes are accepted to decompress.
    """
    string = "The quick brown fox jumps over the lazy dog."
    size = 1
    with pytest.raises(TypeError):
        unishox2.decompress(string, size)
    with pytest.raises(TypeError):
        unishox2.decompress([string], size)
    with pytest.raises(TypeError):
        unishox2.decompress((string,), size)
    with pytest.raises(TypeError):
        unishox2.decompress({"string": string}, size)
    with pytest.raises(TypeError):
        unishox2.decompress(1, size)
    with pytest.raises(TypeError):
        unishox2.decompress(1.5, size)


def test_decompress_non_int():
    """
    Verify only integers are accepted by decompress for malloc()

    A NEGATIVE INTEGER WILL CAUSE A FAILURE!
    """
    string = "The quick brown fox jumps over the lazy dog."
    byte = b"\x87\xa7=\xe3\xe5y\x95=\xa5^/y\xfd\xbfi&\x8c\xb0\x1fy\x95\x7f\x11w\x8a{&\xd7\xbc\xf5\x93\xdaI\x97"
    size = 1
    with pytest.raises(TypeError):
        unishox2.decompress(byte, string)
    with pytest.raises(TypeError):
        unishox2.decompress(byte, [size])
    with pytest.raises(TypeError):
        unishox2.decompress(byte, (size,))
    with pytest.raises(TypeError):
        unishox2.decompress(byte, {"size": size})
    with pytest.raises(TypeError):
        unishox2.decompress(byte, 1.5)


def test_surrogate_fails():
    """
    Ensure that a UnicodeEncodeError is thrown when a surrogate is used.
    """
    surrogate = "\ud800"
    with pytest.raises(UnicodeEncodeError):
        compressed, original_size = unishox2.compress(surrogate)


@pytest.mark.parametrize(
    "string",
    [
        "Hello",
        "Hello World",
        "The quick brown fox jumped over the lazy dog",
        "HELLO WORLD",
        "HELLO WORLD HELLO WORLD",
        "Hello1",
        "Hello1 World2",
        "Hello123",
        "12345678",
        "12345678 12345678",
        "HELLO WORLD 1234 hello world12",
        "HELLO 234 WORLD",
        "9 HELLO, WORLD",
        "H1e2l3l4o5 w6O7R8L9D",
        "8+80=88",
        "~!@#$%^&*()_+=-`;'\\|\":,./?><",
        'if (!test_ushx_cd("H1e2l3l4o5 w6O7R8L9D",',
        "Hello\tWorld\tHow\tare\tyou?",
        "Hello~World~How~are~you?",
        "Hello\rWorld\rHow\rare\ryou?",
        "-----------------///////////////",
        "-----------------Hello World1111111111112222222abcdef12345abcde1234_////////Hello World///////",
        "fa01b51e-7ecc-4e3e-be7b-918a4c2c891c",
        "Fa01b51e-7ecc-4e3e-be7b-918a4c2c891c",
        "fa01b51e-7ecc-4e3e-be7b-9182c891c",
        "760FBCA3-272E-4F1A-BF88-8472DF6BD994",
        "760FBCA3-272E-4F1A-BF88-8472DF6Bd994",
        "760FBCA3-272E-4F1A-BF88-8472DF6Bg994",
        "FBCA3-272E-4F1A-BF88-8472DF6BD994",
        "Hello 1 5347a688-d8bf-445d-86d1-b470f95b007fHello World",
        "01234567890123",
        "2020-12-31",
        "1934-02",
        "2020-12-31T12:23:59.234Z",
        "1899-05-12T23:59:59.23434",
        "1899-05-12T23:59:59",
        "2020-12-31T12:23:59.234Zfa01b51e-7ecc-4e3e-be7b-918a4c2c891c",
        "顔に(993) 345-3495あり",
        "HELLO(993) 345-3495WORLD",
        "顔に1899-05-12T23:59:59あり",
        "HELLO1899-05-12T23:59:59WORLD",
        "Cada buhonero alaba sus agujas. - A peddler praises his needles (wares).",
        "Cada gallo canta en su muladar. - Each rooster sings on its dung-heap.",
        "Cada martes tiene su domingo. - Each Tuesday has its Sunday.",
        "Cada uno habla de la feria como le va en ella. - Our way of talking about things reflects our relevant experience, good or bad.",
        "Dime con quien andas y te diré quién eres.. - Tell me who you walk with, and I will tell you who you are.",
        "Donde comen dos, comen tres. - You can add one person more in any situation you are managing.",
        "El amor es ciego. - Love is blind",
        "El amor todo lo iguala. - Love smoothes life out.",
        "El tiempo todo lo cura. - Time cures all.",
        "La avaricia rompe el saco. - Greed bursts the sack.",
        "La cara es el espejo del alma. - The face is the mirror of the soul.",
        "La diligencia es la madre de la buena ventura. - Diligence is the mother of good fortune.",
        "La fe mueve montañas. - Faith moves mountains.",
        "La mejor palabra siempre es la que queda por decir. - The best word is the one left unsaid.",
        "La peor gallina es la que más cacarea. - The worst hen is the one that clucks the most.",
        "La sangre sin fuego hierve. - Blood boils without fire.",
        "La vida no es un camino de rosas. - Life is not a path of roses.",
        "Las burlas se vuelven veras. - Bad jokes become reality.",
        "Las desgracias nunca vienen solas. - Misfortunes never come one at a time.",
        "Lo comido es lo seguro. - You can only be really certain of what is already in your belly.",
        "Los años no pasan en balde. - Years don't pass in vain.",
        "Los celos son malos consejeros. - Jealousy is a bad counsellor.",
        "Los tiempos cambian. - Times change.",
        "Mañana será otro día. - Tomorrow will be another day.",
        "Ningún jorobado ve su joroba. - No hunchback sees his own hump.",
        "No cantan dos gallos en un gallinero. - Two roosters do not crow in a henhouse.",
        "No hay harina sin salvado. - No flour without bran.",
        "No por mucho madrugar, amanece más temprano.. - No matter if you rise early because it does not sunrise earlier.",
        "No se puede hacer tortilla sin romper los huevos. - One can't make an omelette without breaking eggs.",
        "No todas las verdades son para dichas. - Not every truth should be said.",
        "No todo el monte es orégano. - The whole hillside is not covered in spice.",
        "Nunca llueve a gusto de todos. - It never rains to everyone's taste.",
        "Perro ladrador, poco mordedor.. - A dog that barks often seldom bites.",
        "Todos los caminos llevan a Roma. - All roads lead to Rome.",
        "案ずるより産むが易し。 - Giving birth to a baby is easier than worrying about it.",
        "出る杭は打たれる。 - The stake that sticks up gets hammered down.",
        "知らぬが仏。 - Not knowing is Buddha. - Ignorance is bliss.",
        "見ぬが花。 - Not seeing is a flower. - Reality can't compete with imagination.",
        "花は桜木人は武士 - Of flowers, the cherry blossom; of men, the warrior.",
        "小洞不补，大洞吃苦 - A small hole not mended in time will become a big hole much more difficult to mend.",
        "读万卷书不如行万里路 - Reading thousands of books is not as good as traveling thousands of miles",
        "福无重至,祸不单行 - Fortune does not come twice. Misfortune does not come alone.",
        "风向转变时,有人筑墙,有人造风车 - When the wind changes, some people build walls and have artificial windmills.",
        "父债子还 - Father's debt, son to give back.",
        "害人之心不可有 - Do not harbour intentions to hurt others.",
        "今日事，今日毕 - Things of today, accomplished today.",
        "空穴来风,未必无因 - Where there's smoke, there's fire.",
        "良药苦口 - Good medicine tastes bitter.",
        "人算不如天算 - Man proposes and God disposes",
        "师傅领进门，修行在个人 - Teachers open the door. You enter by yourself.",
        "授人以鱼不如授之以渔 - Teach a man to take a fish is not equal to teach a man how to fish.",
        "树倒猢狲散 - When the tree falls, the monkeys scatter.",
        "水能载舟，亦能覆舟 - Not only can water float a boat, it can sink it also.",
        "朝被蛇咬，十年怕井绳 - Once bitten by a snake for a snap dreads a rope for a decade.",
        "一分耕耘，一分收获 - If one does not plow, there will be no harvest.",
        "有钱能使鬼推磨 - If you have money you can make the devil push your grind stone.",
        "一失足成千古恨，再回头已百年身 - A single slip may cause lasting sorrow.",
        "自助者天助 - Those who help themselves, God will help.",
        "早起的鸟儿有虫吃 - Early bird gets the worm.",
        "This is first line,\r\nThis is second line",
        '{"menu": {\n  "id": "file",\n  "value": "File",\n  "popup": {\n    "menuitem": [\n      {"value": "New", "onclick": "CreateNewDoc()"},\n      {"value": "Open", "onclick": "OpenDoc()"},\n      {"value": "Close", "onclick": "CloseDoc()"}\n    ]\n  }\n}}',
        '{"menu": {\r\n  "id": "file",\r\n  "value": "File",\r\n  "popup": {\r\n    "menuitem": [\r\n      {"value": "New", "onclick": "CreateNewDoc()"},\r\n      {"value": "Open", "onclick": "OpenDoc()"},\r\n      {"value":"Close", "onclick": "CloseDoc()"}\r\n    ]\r\n  }\r\n}}',
        "https://siara.cc",
        '符号"δ"表',
        "学者地”[3]。学者",
        "한데......아무",
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
        "🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣",
        "😀😃😄😁😆😅🤣😂🙂🙃😉😊😇🥰😍🤩😘😗😚😙😋😛😜🤪😝🤑🤗🤭🤫🤔🤐🤨😐😑😶😏😒🙄😬🤥😌😔😪🤤😴😷🤒🤕🤢",
        "Hello\x80\x83\xAE\xBC\xBD\xBE",
    ],
)
def test_original_suite(string):
    """
    Verify functionality based on the original test_unishox2.c
    https://github.com/siara-cc/Unishox/blob/d8fafe350446e4be3a05e06a0404a2223d4d972d/test_unishox2.c
    """
    compressed, original_size = unishox2.compress(string)
    decompressed = unishox2.decompress(compressed, original_size)
    assert decompressed == string


@pytest.mark.parametrize(
    "string",
    [
        "^",
        "e",
        "8Z",
        "q8Z",
        "q%8Z",
        "^r%u7nW",
        "i7F%R2G!R",
        "s2S2HCS&^$iT",
        "WuA4L9Kt^w9M%eXnUWe^",
        "*$@gHRe%GbhdXw!oE*#smi9x7VFF",
        "2DdWCAy5xX$Po*p3ZNz%cC6nHee9kP8mowB4#ioAEq5^CG",
        "Hg@hF&6v^DrV^MDRV&&t4ieSJWFEUGFUf9raVX2^@M2iKgVgCia$9AY*A^XgJyjrtW2UKkLM6nHgD&VGWqjg*rgBPKhdZShsKc#T69e%Zy#wvr6af!BFdZQa%wFdX669(",
    ],
)
def test_high_entropy(string):
    """
    Unishox2 seems to struggle in rare cases that data is extremely high entropy.
    """
    compressed, original_size = unishox2.compress(string)
    decompressed = unishox2.decompress(compressed, original_size)
    assert decompressed == string


@pytest.mark.parametrize(
    "string",
    [
        "Test ASCII inputs.",
        "~!@#$%^&*()_+=-`;'\\|\":,./?><",
        "*$@gHRe%GbhdXw!oE*#smi9x7VFF",
        'if (!test_ushx_cd("H1e2l3l4o5 w6O7R8L9D",',
        "The quick brown fox jumps over the lazy dog.",
        "https://chris.partridge.tech",
    ],
)
def test_ascii_encoded_string(string):
    """
    Unishox2 seems to handle ASCII inputs fine as well if you have them.
    """
    compressed, original_size = unishox2.compress(string.encode("ascii"))
    decompressed = unishox2.decompress(compressed, original_size)
    assert decompressed == string


@given(integers(min_value=44, max_value=1073741824))
@settings(max_examples=2500)
def test_decompress_with_malloc_up_to_1gb(alloc):
    """
    Ensures that as long as a *minimum* length is known for strings,
    decompression will always work, and original_size doesn't need to be saved.
    """
    string = "The quick brown fox jumps over the lazy dog."
    compressed, original_size = unishox2.compress(string)
    decompressed = unishox2.decompress(compressed, alloc)
    assert decompressed == string


@given(text())
@settings(max_examples=25000)
def test_random_unicode_strings(string):
    """
    Verify all sorts of strings, generated by hypothesis.
    This includes empty strings, very long strings, various kinds of Unicode
    characters etc.
    """
    compressed, original_size = unishox2.compress(string)
    decompressed = unishox2.decompress(compressed, original_size)
    assert decompressed == string
