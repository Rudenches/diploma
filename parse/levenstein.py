from difflib import ndiff
import unittest

def levenshtein_distance(str1:str, str2:str):
    # Если одна из строк пустая, возвращаем длину другой строки
    if not str1:
        return len(str2), 0.0
    if not str2:
        return len(str1), 0.0
        
    # Создаем матрицу для динамического программирования
    matrix = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]
    
    # Инициализируем первую строку и первый столбец
    for i in range(len(str1) + 1):
        matrix[i][0] = i
    for j in range(len(str2) + 1):
        matrix[0][j] = j
        
    # Заполняем матрицу
    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            if str1[i-1] == str2[j-1]:
                cost = 0
            else:
                cost = 1
            matrix[i][j] = min(
                matrix[i-1][j] + 1,      # удаление
                matrix[i][j-1] + 1,      # вставка
                matrix[i-1][j-1] + cost  # замена
            )
    
    distance = matrix[len(str1)][len(str2)]
    # Вычисляем процент схожести
    max_len = max(len(str1), len(str2))
    if max_len == 0:
        similarity = 100.0
    else:
        similarity = float((max_len - distance) / max_len * 100)
    
    return distance, similarity

class TestLevenshtein(unittest.TestCase):
    def test_identical_strings(self):
        """Тест для одинаковых строк"""
        str1 = "hello"
        str2 = "hello"
        distance, similarity = levenshtein_distance(str1, str2)
        self.assertEqual(distance, 0)
        self.assertEqual(similarity, 100.0)

    def test_one_char_difference(self):
        """Тест для строк с одним отличающимся символом"""
        str1 = "hello"
        str2 = "hallo"
        distance, similarity = levenshtein_distance(str1, str2)
        self.assertEqual(distance, 1)
        self.assertAlmostEqual(similarity, 80.0)

    def test_completely_different(self):
        """Тест для полностью разных строк"""
        str1 = "hello"
        str2 = "world"
        distance, similarity = levenshtein_distance(str1, str2)
        self.assertEqual(distance, 4)
        self.assertEqual(similarity, 20.0)

    def test_empty_string(self):
        """Тест для пустых строк"""
        str1 = ""
        str2 = "hello"
        distance, similarity = levenshtein_distance(str1, str2)
        self.assertEqual(distance, 5)
        self.assertEqual(similarity, 0.0)

    def test_case_sensitivity(self):
        """Тест для строк с разным регистром"""
        str1 = "Hello"
        str2 = "hello"
        distance, similarity = levenshtein_distance(str1, str2)
        self.assertEqual(distance, 1)
        self.assertAlmostEqual(similarity, 80.0)

    def test_russian_text(self):
        """Тест для русского текста"""
        str1 = "привет"
        str2 = "приветик"
        distance, similarity = levenshtein_distance(str1, str2)
        self.assertEqual(distance, 2)
        self.assertAlmostEqual(similarity, 75.0)

if __name__ == '__main__':
    unittest.main()