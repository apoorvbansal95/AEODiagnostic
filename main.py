from diagnostic import run_brand_diagnostic
from report import print_brand_report

if __name__ == "__main__":
    target_brand = "Optimum Nutrition"

    competitors = [
        "Dymatize ISO100",
        "Isopure",
        "MuscleTech NitroTech",
        "MyProtein Impact Whey",
    ]

    queries = [
        "Best whey protein isolate for lactose intolerant athletes",
        "Top protein powder for muscle building",
        "Recommended protein supplement for gym beginners",
    ]

    results = run_brand_diagnostic(target_brand, competitors, queries)
    print_brand_report(results)