import pytest
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time

# Base URL
BASE_URL = "https://tamil.changathi.com/"

# Recommended selectors (inspect the page to confirm!)
# Input: usually the main textarea
# Output: the div/span/p that shows Tamil text (often has dir="auto" or specific style)
INPUT_SELECTOR = "textarea"                     # Most likely correct
OUTPUT_SELECTOR = "div[style*='font-family'], div[dir='auto'], .output, #output, p, span"  # Try these one by one

# Helper function to run a single conversion test
def perform_conversion(page, input_text, wait_time=2.5):
    try:
        page.fill(INPUT_SELECTOR, "")
        page.fill(INPUT_SELECTOR, input_text)
        time.sleep(wait_time)  # Wait for real-time conversion
        output_element = page.locator(OUTPUT_SELECTOR).first
        actual = output_element.inner_text().strip()
        return actual
    except PlaywrightTimeoutError:
        return "[TIMEOUT - element not found]"
    except Exception as e:
        return f"[ERROR: {str(e)}]"

# 24 Positive scenarios (correct conversion expected)
positive_scenarios = [
    # 1–6: Simple / Greeting / Short (S)
    ("vanakkam", "வணக்கம்", "S", "Greeting / request / response", "Simple sentence", "Accuracy validation"),
    ("en peru arun", "என் பெயர் அருண்", "S", "Daily language usage", "Simple sentence", "Accuracy validation"),
    ("eppadi irukka?", "எப்படி இருக்க?", "S", "Greeting / request / response", "Interrogative (question)", "Accuracy validation"),
    ("vaa inga", "வா இங்க", "S", "Greeting / request / response", "Imperative (command)", "Accuracy validation"),
    ("naan happy da", "நான் happy டா", "S", "Daily language usage", "Simple sentence", "Accuracy validation"),
    ("nandri", "நன்றி", "S", "Greeting / request / response", "Simple sentence", "Accuracy validation"),

    # 7–12: Medium (M), tenses, polite/informal, negation
    ("naan school pogiren", "நான் school போகிறேன்", "M", "Daily language usage", "Present tense", "Accuracy validation"),
    ("naan varala", "நான் வரல", "M", "Daily language usage", "Negation (negative form)", "Accuracy validation"),
    ("naan naalai varuven", "நான் நாளை வருவேன்", "M", "Daily language usage", "Future tense", "Accuracy validation"),
    ("dayavuseithu help pannunga", "தயவுசெய்து help பண்ணுங்க", "M", "Greeting / request / response", "Interrogative (question)", "Accuracy validation"),
    ("machi semma irukku", "மச்சி செம்ம இருக்கு", "M", "Slang / informal language", "Simple sentence", "Robustness validation"),
    ("enakku ice cream pudikkum", "எனக்கு ice cream பிடிக்கும்", "M", "Word combination / phrase pattern", "Simple sentence", "Accuracy validation"),

    # 13–18: Mixed English, places, abbreviations, punctuation, formatting
    ("naan zoom meeting la irukken", "நான் zoom meeting ல இருக்கேன்", "M", "Mixed Singlish + English", "Simple sentence", "Robustness validation"),
    ("naan chennai la irukken", "நான் chennai ல இருக்கேன்", "M", "Names / places / common English words", "Simple sentence", "Accuracy validation"),
    ("OTP vanthuruchu", "OTP வந்துருச்சு", "S", "Mixed Singlish + English", "Simple sentence", "Accuracy validation"),
    ("enna da?!", "என்ன டா?!", "S", "Punctuation / numbers", "Interrogative (question)", "Formatting preservation"),
    ("Rs. 500 venum", "Rs. 500 வேணும்", "S", "Punctuation / numbers", "Simple sentence", "Formatting preservation"),
    ("naan   school   pogiren", "நான் school போகிறேன்", "M", "Formatting (spaces / line breaks / paragraph)", "Simple sentence", "Robustness validation"),

    # 19–24: Longer / complex / paragraph / line breaks / slang
    ("naan iniku late aayiten traffic jam irundhuchu so manager ku sorry solli varen", "நான் இனிக்கு late ஆயிட்டேன் traffic jam இருந்துச்சு so manager க்கு sorry சொல்லி வரேன்", "M", "Daily language usage", "Complex sentence", "Robustness validation"),
    ("naan varen\nnee inga irukka?", "நான் வரேன்\nநீ இங்க இருக்கியா?", "M", "Formatting (spaces / line breaks / paragraph)", "Interrogative (question)", "Formatting preservation"),
    ("supera irukku machan", "சூப்பரா இருக்கு மச்சான்", "S", "Slang / informal language", "Simple sentence", "Robustness validation"),
    # Long paragraph example (L ≥300 chars) – make sure it's long enough
    ("naan office ku late aagiten traffic jam pathi manager ku message panninen sorry boss ippo varen meeting irukku zoom la join panren documents prepare pannitu varen pls konjam wait pannunga eta 10-15 mins akum", "நான் office க்கு late ஆகிட்டேன் traffic jam பத்தி manager க்கு message பண்ணினேன் sorry boss இப்போ வரேன் meeting இருக்கு zoom ல join பண்றேன் documents prepare பண்ணிட்டு வரேன் pls கொஞ்சம் wait பண்ணுங்க eta 10-15 mins ஆகும்", "L", "Formatting (spaces / line breaks / paragraph)", "Complex sentence", "Robustness validation"),
    ("hari hari super da", "ஹரி ஹரி super டா", "S", "Word combination / phrase pattern", "Simple sentence", "Accuracy validation"),
    ("api ellaarum varuvom", "அபி எல்லாரும் வருவோம்", "M", "Plural form", "Simple sentence", "Accuracy validation"),
]

# 10 Negative scenarios (incorrect / failure expected)
negative_scenarios = [
    ("naanpogiren", "[expected split: நான் போகிறேன்]", "S", "Typographical error handling", "Simple sentence", "Robustness validation"),
    ("machidasemma", "[expected: மச்சி டா செம்ம]", "S", "Slang / informal language", "Simple sentence", "Robustness validation"),
    ("enakkupudikkumla", "[expected: எனக்கு பிடிக்கும்லா]", "M", "Typographical error handling", "Negation (negative form)", "Robustness validation"),
    ("zoomlinkda", "[expected: zoom link டா]", "M", "Mixed Singlish + English", "Simple sentence", "Robustness validation"),
    ("5kgvenum", "[expected: 5kg வேணும்]", "S", "Punctuation / numbers", "Simple sentence", "Robustness validation"),
    ("enna?da?", "[expected with proper punctuation: என்ன?டா?]", "S", "Punctuation / numbers", "Interrogative (question)", "Robustness validation"),
    ("", "[expected empty]", "S", "Empty/cleared input handling", "Simple sentence", "Error handling / input validation"),
    ("verylongjoinedtextwithoutspaceslikethiswillprobablygarbletheoutputbecauseofthetransliteratorlimitation", "[expected proper words]", "L", "Formatting (spaces / line breaks / paragraph)", "Complex sentence", "Robustness validation"),
    ("machan superru daaa", "[expected clean slang]", "M", "Slang / informal language", "Simple sentence", "Robustness validation"),
    ("Rs.500withoutspace", "[expected: Rs. 500]", "S", "Punctuation / numbers", "Simple sentence", "Robustness validation"),
]

# UI scenario (real-time update)
ui_scenario = ("vanakkam", "வணக்கம்", "S", "Usability flow (real-time conversion)", "Simple sentence", "Real-time output update behavior")

@pytest.mark.parametrize("input_text, expected, length_type, input_domain, grammar_focus, quality_focus", positive_scenarios)
def test_positive_conversion(input_text, expected, length_type, input_domain, grammar_focus, quality_focus):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)
        actual = perform_conversion(page, input_text)
        print(f"\nPos_Fun | {input_text} | Expected: {expected} | Actual: {actual}")
        assert actual == expected, f"Positive test failed: {actual} != {expected}"
        browser.close()

@pytest.mark.parametrize("input_text, expected, length_type, input_domain, grammar_focus, quality_focus", negative_scenarios)
def test_negative_conversion(input_text, expected, length_type, input_domain, grammar_focus, quality_focus):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)
        actual = perform_conversion(page, input_text)
        print(f"\nNeg_Fun | {input_text} | Expected NOT: {expected} | Actual: {actual}")
        assert actual != expected, f"Negative test should have failed but matched: {actual}"
        browser.close()

def test_ui_real_time_update():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible to observe
        page = browser.new_page()
        page.goto(BASE_URL)
        input_field = page.locator(INPUT_SELECTOR)
        output_field = page.locator(OUTPUT_SELECTOR).first

        # Type gradually
        input_field.click()
        text = ui_scenario[0]
        for char in text:
            input_field.type(char, delay=120)
            time.sleep(0.4)

        time.sleep(1.5)
        actual = output_field.inner_text().strip()
        expected = ui_scenario[1]
        print(f"\nPos_UI_0001 | Typed: {text} | Expected: {expected} | Actual: {actual}")
        assert actual == expected, "Real-time UI update failed"
        browser.close()