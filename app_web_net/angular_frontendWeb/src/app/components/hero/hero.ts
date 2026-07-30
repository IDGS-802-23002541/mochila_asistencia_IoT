import { AfterViewInit, Component } from '@angular/core';

@Component({
  selector: 'app-hero',
  imports: [],
  templateUrl: './hero.html',
  styleUrl: './hero.css',
})
export class Hero implements AfterViewInit{
  ngAfterViewInit(): void {
    this.initCounters();
  }

  private initCounters(): void {

    const animateCounter = (el: HTMLElement) => {

      const target = parseFloat(el.dataset['target'] || '0');
      const prefix = el.dataset['prefix'] || '';
      const suffix = el.dataset['suffix'] || '';
      const decimal = parseInt(el.dataset['decimal'] || '0');

      const duration = 2000;
      const start = performance.now();

      const update = (currentTime: number) => {

        const progress = Math.min((currentTime - start) / duration, 1);
        const value = target * progress;

        el.textContent =
          prefix +
          (decimal ? value.toFixed(decimal) : Math.floor(value)) +
          suffix;

        if (progress < 1) {
          requestAnimationFrame(update);
        }
      };

      requestAnimationFrame(update);

    };

    const statsSection = document.querySelector('.hero-stats');

    if (!statsSection) return;

    const observer = new IntersectionObserver((entries) => {

      entries.forEach(entry => {

        if (entry.isIntersecting) {

          const counters = statsSection.querySelectorAll<HTMLElement>('.stat-num');

          counters.forEach(counter => {

            if (!counter.dataset['animated']) {

              counter.dataset['animated'] = 'true';
              animateCounter(counter);

            }

          });

          observer.disconnect();

        }

      });

    }, {
      threshold: 0.3
    });

    observer.observe(statsSection);

  }

}
