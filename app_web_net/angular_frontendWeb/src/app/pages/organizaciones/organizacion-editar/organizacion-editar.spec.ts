import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OrganizacionEditar } from './organizacion-editar';

describe('OrganizacionEditar', () => {
  let component: OrganizacionEditar;
  let fixture: ComponentFixture<OrganizacionEditar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrganizacionEditar],
    }).compileComponents();

    fixture = TestBed.createComponent(OrganizacionEditar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
