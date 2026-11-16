import json

from django.test import TestCase, override_settings

from myapp.models import StockInfo

PLAIN_STATIC = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(STORAGES=PLAIN_STATIC)
class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        def stock(name, grade, score, **fields):
            return StockInfo.objects.create(
                name=name,
                company_name=f"{name} Inc",
                industry="Banks - Regional",
                sector="Financial",
                overall_grade=grade,
                overall_grade_num=score,
                pe_grade="B",
                ps_grade="C",
                pb_grade="A",
                prices=[10.0, 11.5, 12.25],
                dates=["2026-11-06", "2026-11-09", "2026-11-10"],
                **fields,
            )

        stock("GOOD", "A+", 99.0, peer_groups={"profit_margin": "sector"}, dtc=2.5)
        stock("FINE", "B", 80.0, dtc=12.0)
        stock("MEH", "C", 50.0, dtc=30.0)
        stock("POOR", "D", 20.0)
        stock("BAD", "F-", 1.0, dtc=7.25)
        # Old rows stored prices as a JSON string and may have no AI analysis.
        stock("OLD", "C+", 60.0, gpt_analysis={})
        StockInfo.objects.filter(name="OLD").update(prices=json.dumps([1.0, 2.0, 3.0]))

    def test_index_suggests_the_top_stock(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="GOOD"')

    def test_overview(self):
        response = self.client.get("/overview", {"text": "good"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GOOD Inc")
        self.assertContains(response, '<button class="btn btn-success">A+</button>', html=True)
        self.assertContains(response, "plotly")
        # The profit-margin median is labelled as a sector median; the others aren't.
        self.assertContains(response, ">(sector)</span>", count=1)

    def test_overview_of_old_row_without_ai_analysis(self):
        response = self.client.get("/overview", {"text": "OLD"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "plotly")

    def test_unknown_ticker_is_404(self):
        response = self.client.get("/overview", {"text": "NOPE"})
        self.assertEqual(response.status_code, 404)

    def test_empty_search_goes_home(self):
        self.assertRedirects(self.client.get("/overview"), "/")

    def test_top_rated_is_b_or_better_best_first(self):
        response = self.client.get("/beststocks")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([s.name for s in response.context["best_stock_list"]], ["GOOD", "FINE"])

    def test_low_rated_is_d_or_worse_worst_first(self):
        response = self.client.get("/worststocks")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([s.name for s in response.context["worst_stock_list"]], ["BAD", "POOR"])

    def test_list_columns_line_up(self):
        # Headers are P/E, P/B, P/S; the old template filled them with P/E, P/S, P/B.
        content = self.client.get("/beststocks").content.decode()
        row = content[content.index("GOOD Inc") :]
        self.assertLess(row.index(">B</button>"), row.index(">A</button>"))
        self.assertLess(row.index(">A</button>"), row.index(">C</button>"))

    def test_ads_txt(self):
        response = self.client.get("/ads.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")

    def test_static_pages(self):
        for url in ("/about", "/privacy"):
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertEqual(self.client.get("/404").status_code, 404)

    def test_about_links_to_linkedin_and_contact_page_is_gone(self):
        self.assertContains(self.client.get("/about"), "linkedin.com/in/nick-lasti")
        self.assertEqual(self.client.get("/contact").status_code, 404)
        self.assertNotContains(self.client.get("/"), "./contact")

    def test_short_squeeze_list_is_ranked_by_days_to_cover(self):
        response = self.client.get("/shortsqueeze")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([s.name for s in response.context["stocks"]], ["MEH", "FINE", "BAD", "GOOD"])
        content = response.content.decode()
        self.assertLess(content.index("<td>1</td>"), content.index("MEH Inc"))
        self.assertIn("<td>30.00</td>", content)

    def test_top_rated_rows_are_numbered(self):
        content = self.client.get("/beststocks").content.decode()
        self.assertLess(content.index("<td>1</td>"), content.index("GOOD Inc"))
        self.assertLess(content.index("<td>2</td>"), content.index("FINE Inc"))

    def test_metric_labels_show_the_period(self):
        response = self.client.get("/overview", {"text": "GOOD"})
        for label in ("Revenue Growth (TTM)", "EBITDA Growth (TTM)", "EPS Growth (Fwd)", "P/E (Fwd)", "P/B (MRQ)"):
            self.assertContains(response, label)

    def test_web_app_files(self):
        manifest = self.client.get("/manifest.webmanifest")
        self.assertEqual(manifest["Content-Type"], "application/manifest+json")
        data = json.loads(manifest.content)
        self.assertEqual(data["display"], "standalone")
        self.assertEqual({icon["sizes"] for icon in data["icons"]}, {"192x192", "512x512"})
        worker = self.client.get("/sw.js")
        self.assertEqual(worker["Content-Type"], "text/javascript")
        self.assertIn('addEventListener("fetch"', worker.content.decode())

    def test_every_page_offers_the_home_screen_app(self):
        for url in ("/", "/about", "/beststocks", "/overview?text=GOOD"):
            response = self.client.get(url)
            self.assertContains(response, 'rel="manifest"')
            self.assertContains(response, 'id="install-prompt"')
            self.assertContains(response, '<link href="/static/app.css" rel="stylesheet">')  # phone layout
            self.assertContains(response, 'width=device-width, initial-scale=1')
