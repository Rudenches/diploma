import unittest
from parse.levenstein import levenshtein_distance
from cyrtranslit import to_latin

class TestLevenshteinExtended(unittest.TestCase):
    def setUp(self):
        """Подготовка тестовых данных"""
        self.test_cases = [
            # Базовые тесты
            {
                "name": "identical_strings",
                "str1": "Фаретдинов Р.А.",
                "str2": "Фаретдинов Р.А.",
                "expected_distance": 0,
                "expected_similarity": 100.0
            },
            {
                "name": "one_char_difference",
                "str1": "Фаретдинов Р.А",
                "str2": "Фаретдинов Р.",
                "expected_distance": 1,
                "expected_similarity": 92.86
            },
            # Тесты с транслитерацией
            {
                "name": "transliteration_comparison",
                "str1": "Сушников",
                "str2": to_latin("Сушников", "ru"),
                "expected_distance": 9,
                "expected_similarity": 0.0
            },
            # Тесты с опечатками
            {
                "name": "typo_in_middle",
                "str1": "Фаретдинов",
                "str2": "Фаретдиновв",
                "expected_distance": 1,
                "expected_similarity": 90.91
            },
            {
                "name": "multiple_typos",
                "str1": "Фаретдинов Р.А.",
                "str2": "Фаретдинов Р.А",
                "expected_distance": 1,
                "expected_similarity": 93.33
            },
            # Тесты с пробелами
            {
                "name": "extra_spaces",
                "str1": "Фаретдинов Р.А.",
                "str2": "Фаретдинов  Р.А.",
                "expected_distance": 1,
                "expected_similarity": 93.75
            },
            # Тесты с разным регистром
            {
                "name": "case_difference",
                "str1": "ФАРЕТДИНОВ Р.А.",
                "str2": "Фаретдинов Р.А.",
                "expected_distance": 9,
                "expected_similarity": 40.0
            },
            # Тесты с пустыми строками
            {
                "name": "empty_strings",
                "str1": "",
                "str2": "",
                "expected_distance": 0,
                "expected_similarity": 0.0
            },
            # Тесты с специальными символами
            {
                "name": "special_characters",
                "str1": "Фаретдинов Р.А.",
                "str2": "Фаретдинов Р.А.!",
                "expected_distance": 1,
                "expected_similarity": 93.75
            },
            # Тесты с длинными строками
            {
                "name": "long_strings",
                "str1": "Фаретдинов Р.А. " * 5,
                "str2": "Фаретдинов Р.А. " * 5,
                "expected_distance": 0,
                "expected_similarity": 100.0
            }
        ]

    def test_all_cases(self):
        """Запуск всех тестовых случаев"""
        results = {
            "total": len(self.test_cases),
            "passed": 0,
            "failed": 0,
            "failed_cases": []
        }

        for case in self.test_cases:
            try:
                distance, similarity = levenshtein_distance(case["str1"], case["str2"])
                self.assertAlmostEqual(distance, case["expected_distance"], 
                                     msg=f"Distance mismatch in {case['name']}")
                self.assertAlmostEqual(similarity, case["expected_similarity"], 
                                     places=2, msg=f"Similarity mismatch in {case['name']}")
                results["passed"] += 1
            except AssertionError as e:
                results["failed"] += 1
                results["failed_cases"].append({
                    "name": case["name"],
                    "error": str(e),
                    "str1": case["str1"],
                    "str2": case["str2"],
                    "expected_distance": case["expected_distance"],
                    "expected_similarity": case["expected_similarity"],
                    "actual_distance": distance,
                    "actual_similarity": similarity
                })

        # Вывод статистики
        print("\n=== Тестирование алгоритма Левенштейна ===")
        print(f"Всего тестов: {results['total']}")
        print(f"Успешно пройдено: {results['passed']}")
        print(f"Не пройдено: {results['failed']}")
        print(f"Процент успешных тестов: {(results['passed'] / results['total'] * 100):.2f}%")

        if results["failed_cases"]:
            print("\nНеудачные тесты:")
            for case in results["failed_cases"]:
                print(f"\nТест: {case['name']}")
                print(f"Строка 1: {case['str1']}")
                print(f"Строка 2: {case['str2']}")
                print(f"Ожидаемое расстояние: {case['expected_distance']}")
                print(f"Фактическое расстояние: {case['actual_distance']}")
                print(f"Ожидаемая схожесть: {case['expected_similarity']}")
                print(f"Фактическая схожесть: {case['actual_similarity']}")
                print(f"Ошибка: {case['error']}")

if __name__ == '__main__':
    unittest.main() 