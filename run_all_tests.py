# """
# run_all_tests.py — Run the entire test suite at once
# Usage: python run_all_tests.py
# """

# import unittest
# from test_home              import HomepageTests, NavigationTests, ResponsiveDesignTests, SecurityTests
# from test_appointments      import AppointmentTests
# from test_medicine_reminder import MedicineReminderTests
# from test_diet              import DietCompatibilityTests

# if __name__ == "__main__":
#     loader = unittest.TestLoader()
#     suite  = unittest.TestSuite()

#     # ── Order: base account checks → protected modules ───────
#     suite.addTests(loader.loadTestsFromTestCase(HomepageTests))
#     suite.addTests(loader.loadTestsFromTestCase(NavigationTests))
#     suite.addTests(loader.loadTestsFromTestCase(SecurityTests))
#     suite.addTests(loader.loadTestsFromTestCase(AppointmentTests))
#     suite.addTests(loader.loadTestsFromTestCase(MedicineReminderTests))
#     suite.addTests(loader.loadTestsFromTestCase(DietCompatibilityTests))
#     suite.addTests(loader.loadTestsFromTestCase(ResponsiveDesignTests))

#     runner = unittest.TextTestRunner(verbosity=2)
#     result = runner.run(suite)

#     passed = result.testsRun - len(result.failures) - len(result.errors)

#     print("\n" + "═" * 65)
#     print("  FULL SUITE SUMMARY")
#     print("═" * 65)
#     print(f"  Total tests : {result.testsRun}")
#     print(f"  ✅ Passed   : {passed}")
#     print(f"  ❌ Failures : {len(result.failures)}")
#     print(f"  💥 Errors   : {len(result.errors)}")
#     print("═" * 65)

#     if result.failures:
#         print("\n  FAILURES:")
#         for test, tb in result.failures:
#             print(f"    ✗ {test}")
#             print(f"      {tb.splitlines()[-1]}")

#     if result.errors:
#         print("\n  ERRORS:")
#         for test, tb in result.errors:
#             print(f"    ✗ {test}")
#             print(f"      {tb.splitlines()[-1]}")

#     exit(0 if result.wasSuccessful() else 1)
