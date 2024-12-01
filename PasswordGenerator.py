import random
import string

class PasswordGenerator:
    def __init__(self, min_len:int = 6, max_len:int = 16, min_special_chars: int = 2, min_uppercase_chars: int = 1, min_numbers: int = 2 ):
        self.minlen = min_len
        self.maxlen = max_len
        self.minnumbers = min_numbers
        self.minschars = min_special_chars
        self.minuchars = min_uppercase_chars

    
    def generate(self):
        # Build character pools
        numbers = [random.choice(string.digits) for _ in range(self.minnumbers)]
        schars = [random.choice(string.punctuation) for _ in range(self.minschars)]
        uchars = [random.choice(string.ascii_uppercase) for _ in range(self.minuchars)]
        lchars_needed = max(self.minlen - len(numbers) - len(schars) - len(uchars), 0)
        lchars = [random.choice(string.ascii_lowercase) for _ in range(lchars_needed)]

        # Combine all characters and shuffle
        password_list = numbers + schars + uchars + lchars
        if len(password_list) < self.minlen:
            password_list += random.choices(
                string.ascii_letters + string.digits + string.punctuation,
                k=self.minlen - len(password_list)
            )

        random.shuffle(password_list)
        password = ''.join(password_list[:self.maxlen])

        return password
