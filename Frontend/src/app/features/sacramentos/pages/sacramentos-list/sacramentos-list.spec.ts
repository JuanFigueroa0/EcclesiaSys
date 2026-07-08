import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SacramentosList } from './sacramentos-list';

describe('SacramentosList', () => {
  let component: SacramentosList;
  let fixture: ComponentFixture<SacramentosList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SacramentosList],
    }).compileComponents();

    fixture = TestBed.createComponent(SacramentosList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
