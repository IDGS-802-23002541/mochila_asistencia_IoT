import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DispositivoDetalle } from './detalle-dispositivo';

describe('DispositivoDetalle', () => {
  let component: DispositivoDetalle;
  let fixture: ComponentFixture<DispositivoDetalle>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DispositivoDetalle],
    }).compileComponents();

    fixture = TestBed.createComponent(DispositivoDetalle);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
