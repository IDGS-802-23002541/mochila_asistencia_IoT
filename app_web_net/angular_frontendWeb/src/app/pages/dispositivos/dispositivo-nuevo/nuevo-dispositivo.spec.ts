import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NuevoDispositivo } from './nuevo-dispositivo';

describe('NuevoDispositivo', () => {
  let component: NuevoDispositivo;
  let fixture: ComponentFixture<NuevoDispositivo>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NuevoDispositivo],
    }).compileComponents();

    fixture = TestBed.createComponent(NuevoDispositivo);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
