# Design proposal - Asystent diety
> Wojciech Kołodziejak 310747
> Mateusz Maj 310826
> Korneliusz Litman 310804

## 1. Harmonogram projektu z podziałem na tygodnie i planowanymi postępami projektu per tydzień
* 30.10 - 12.11: Przygotowanie struktury bazy danych
* 13.11 - 19.11: Implementacja algorytmu generowania planu diety.
* 20.11 - 27.11: Przygotowanie specyfikacji OpenAPI w Swaggerze i mechanizmów zbierania logów
* 28.11 - 10.12: Implementacja API/frontendu
* 11.12 - 24.12: Implementacja testów jednostkowych i wydajnościowych
* 1.01 - 7.01 - Konteneryzacja i wdrożenie produkcyjne
* 8.01 - 14.01 - Ostatnia faza testów, oddanie projektu

## 2. Bibliografia

* [Dokumentacja Python](https://docs.python.org/3/)
* [Dokumentacja Django](https://docs.djangoproject.com/en/)
* [Dokumentacja Celery](https://docs.celeryq.dev/en/stable/)
* [Dokumentacja Redis](https://redis.io/docs/about/)
* [Dokumentacja pytest](https://docs.pytest.org/en/)
* [Dokumentacja Django Rest Framework](https://www.django-rest-framework.org/)
* [Dokumentacja locust](https://docs.locust.io/en/stable/)
* [Dokumentacja PostgreSQL](https://www.postgresql.org/docs/)
* [Dokumentacja Docker](https://docs.docker.com/)
* [Dokumentacja Sentry](https://docs.sentry.io/)

## 3. Planowana funkcjonalność programu
* Rejestracja użytkownika - użytkownik zanim będzie mógł wygenerować plan diety będzie musiał się na początku zarejestrować

* Generowanie personalnych planów dietetycznych - zarejestrowany użytkownik będzie proszony o podanie następujących parametrów:
    * liczba dni
    * liczba dań na dzień
    * preferowany typ kuchni
    * składniki "zabronione"
    * preferowana ilość kalorii

    Następnie na ich podstawie oraz algorytmu będzie generowany asynchronicznie plan diety, który następnie będzie przechowywany w bazie.

* Wyświetlanie planów - każdy użytkownik będzie miał dostęp do przeglądania swoich planów oraz potencjalnej ich modyfikacji.

Pobieranie parametrów będzie odbywało się poprzez prosty frontend i wysyłane na backend. Następnie frontend przy użyciu long pollingu będzie odpytywać o status generowanego planu diety. Gdy będzie on gotowy, nastąpi zmiana statusu oraz wyświetlenie planu użytkownikowi.

Cała aplikacja zostanie skonteneryzowana w celu szybkiego, zautomatyzowanego wdrożenia. Oprócz tego funkcjonalności aplikacji zostaną przetestowane korzystając z testów jednostkowych oraz wydajnościowych.

## 4. Planowany stack technologiczny
* Backend
    * Python
    * Django + Django Rest Framework
    * pytest + locust
    * Celery + Redis
* Frontend
    * JavaScript + TypeScript
    * React
    * Tailwind + daisyUI
* Docker + Kubernetes
* PostgreSQL
* Sentry



