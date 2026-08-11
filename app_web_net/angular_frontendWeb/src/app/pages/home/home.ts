import { Component } from '@angular/core';

import { Navbar } from '../../components/navbar/navbar';
import { Hero } from '../../components/hero/hero';
import { Services } from '../../components/services/services';
import { Quotation } from '../../components/quotation/quotation';
import { Contact } from '../../components/contact/contact';
import { Footer } from '../../components/footer/footer';
import { Faq } from '../../components/faq/faq';

@Component({
  selector: 'app-home',
  imports: [
    Navbar,
    Hero,
    Services,
    Quotation,
    Faq,
    Contact,
    Footer
  ],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home {

}
