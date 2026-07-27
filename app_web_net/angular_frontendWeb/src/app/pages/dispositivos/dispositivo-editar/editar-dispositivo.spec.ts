import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditarDispositivo } from './editar-dispositivo';

describe('EditarDispositivo', () => {
  let component: EditarDispositivo;
  let fixture: ComponentFixture<EditarDispositivo>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditarDispositivo],
    }).compileComponents();

    fixture = TestBed.createComponent(EditarDispositivo);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
