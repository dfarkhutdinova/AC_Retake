import os
import subprocess

TESTS_DIR = 'tests'
OUTPUT_FILE = 'test_results.txt'

def run_test(file_path):
    try:
        result = subprocess.run(
            ['python', 'interpret.py', file_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, '', str(e)

def run_tests_in_dir(dir_path, expected_success=True, results_file=None):
    passed_tests = 0
    failed_tests = 0
    results = []

    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".stella"):
                file_path = os.path.join(root, file)
                return_code, stdout, stderr = run_test(file_path)

                if expected_success and return_code == 0:
                    results.append(f"Тест {file} пройден успешно.")
                    passed_tests += 1
                elif not expected_success and return_code != 0:
                    results.append(f"Тест {file} правильно вызвал ошибку.")
                    passed_tests += 1
                else:
                    if expected_success:
                        results.append(f"Тест {file} должен был пройти, но произошла ошибка!\nstdout: {stdout}\nstderr: {stderr}")
                    else:
                        results.append(f"Тест {file} должен был завершиться ошибкой, но прошел успешно!\nstdout: {stdout}\nstderr: {stderr}")
                    failed_tests += 1

    if results_file:
        with open(results_file, 'a') as f:
            f.write(f"\nЗапуск тестов в директории: {dir_path}\n")
            for result in results:
                f.write(result + '\n')

    return passed_tests, failed_tests

def run_all_tests():
    with open(OUTPUT_FILE, 'w') as f:
        f.write("Результаты тестов:\n")

    for subdir in os.listdir(TESTS_DIR):
        subdir_path = os.path.join(TESTS_DIR, subdir)

        if os.path.isdir(subdir_path):
            well_typed_path = os.path.join(subdir_path, 'well-typed')
            ill_typed_path = os.path.join(subdir_path, 'ill-typed')

            total_passed = 0
            total_failed = 0

            if os.path.exists(well_typed_path):
                passed, failed = run_tests_in_dir(well_typed_path, expected_success=True, results_file=OUTPUT_FILE)
                total_passed += passed
                total_failed += failed

            if os.path.exists(ill_typed_path):
                passed, failed = run_tests_in_dir(ill_typed_path, expected_success=False, results_file=OUTPUT_FILE)
                total_passed += passed
                total_failed += failed

            if total_failed == 0:
                print(f"{subdir}: correct!")
            else:
                print(f"{subdir}: есть ошибки, passed: {total_passed} tests, failed: {total_failed} tests, подробности см. в {OUTPUT_FILE}")

if __name__ == "__main__":
    run_all_tests()
