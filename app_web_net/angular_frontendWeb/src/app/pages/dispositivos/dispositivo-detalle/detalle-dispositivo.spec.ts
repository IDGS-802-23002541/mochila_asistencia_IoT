import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DetalleDispositivo } from './detalle-dispositivo';

describe('DetalleDispositivo', () => {
  let component: DetalleDispositivo;
  let fixture: ComponentFixture<DetalleDispositivo>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DetalleDispositivo],
    }).compileComponents();

    fixture = TestBed.createComponent(DetalleDispositivo);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
