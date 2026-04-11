import random

def corrupt_text(text, intensity=7):
        result = ""
        
        MARKS_ABOVE  = [chr(i) for i in range(0x0300, 0x036F)]
        MARKS_BELOW  = [chr(i) for i in range(0x0316, 0x032D)]
        MARKS_OVER   = [chr(i) for i in range(0x0334, 0x0338)]
        
        for ch in text:
            result += ch
            for _ in range(intensity):
                result += random.choice(
                    MARKS_ABOVE + MARKS_BELOW + MARKS_OVER
                )
        return result