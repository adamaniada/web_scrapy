import scrapy
import re


class MelbetSpider(scrapy.Spider):
    name = "melbet"
    allowed_domains = ["melbet.com"]
    start_urls = ["https://melbet.com/en/live/fifa"]

    def parse(self, response):
        # Extraction des liens correspondant au pattern /en/live/fifa/{pattern}/{subpattern}
        pattern = re.compile(r"^/en/live/fifa/[^/]+/[^/]+$")
        links = response.css("a::attr(href)").getall()

        for link in links:
            if pattern.match(link):
                full_url = response.urljoin(link)
                # Extraire les informations des équipes à partir de l'URL
                teams = self.extract_teams_from_url(full_url)
                if teams:
                    home_team, away_team = teams
                    # Afficher les informations des équipes
                    self.logger.info(
                        f"URL: {full_url}, Home Team: {home_team}, Away Team: {away_team}"
                    )
                    # Suivre le lien pour extraire les statistiques de l'événement
                    yield scrapy.Request(
                        full_url,
                        callback=self.parse_event,
                        meta={"home_team": home_team, "away_team": away_team},
                    )

    def extract_teams_from_url(self, url):
        # Utiliser une expression régulière pour extraire les équipes de l'URL
        match = re.search(
            r"/en/live/fifa/[^/]+/[^/]+-(?P<home_team>[^-]+)-(?P<away_team>[^/]+)", url
        )
        if match:
            home_team = match.group("home_team").replace("-", " ").title()
            away_team = match.group("away_team").replace("-", " ").title()
            return home_team, away_team
        return None

    def parse_event(self, response):
        home_team = response.meta["home_team"]
        away_team = response.meta["away_team"]

        # Extraire le temps du match
        match_time = response.css("span.game-timer-time__label::text").get()

        # Extraire la période du match
        match_period = response.css(
            "span.game-timer__label.game-timer__label--alone::text"
        ).get()

        # Extraire les scores des équipes
        home_team_score = response.css(
            "span.scoreboard-scores-item-score--team-1::text"
        ).get()
        away_team_score = response.css(
            "span.scoreboard-scores-item-score--team-2::text"
        ).get()

        stats = {
            "home_team": home_team,
            "away_team": away_team,
            "match_time": match_time,
            "match_period": match_period,
            "home_team_score": home_team_score,
            "away_team_score": away_team_score,
        }

        # Afficher les statistiques et le temps du match
        self.logger.info(f"\n\n\nEvent Stats: {stats}")

        # Vous pouvez aussi retourner les stats comme un item si vous utilisez un pipeline de données
        yield stats
