import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OrganizacionNuevo } from './organizacion-nuevo';

describe('OrganizacionNuevo', () => {
  let component: OrganizacionNuevo;
  let fixture: ComponentFixture<OrganizacionNuevo>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrganizacionNuevo],
    }).compileComponents();

    fixture = TestBed.createComponent(OrganizacionNuevo);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
