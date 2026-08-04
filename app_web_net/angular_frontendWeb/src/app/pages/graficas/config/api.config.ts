// Un solo lugar para la URL del backend. Si el puerto cambia algun dia
// (ej. si se despliega a un servidor real), solo se edita aqui -- no en
// cada componente que consume el API.
import { environment } from '../../../../environments/environment';

export const API_BASE_URL = environment.apiUrl;
