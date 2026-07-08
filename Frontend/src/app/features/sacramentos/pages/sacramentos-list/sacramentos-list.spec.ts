import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SacramentosListComponent} from './sacramentos-list';

describe('SacramentosListComponent', () => {
  let component: SacramentosListComponent;
  let fixture: ComponentFixture<SacramentosListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SacramentosListComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SacramentosList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
