using CangureraInteligente.Models;

public class ZonaCaliente
{
    public int Id {get; set;}
    public decimal Latitud {get; set;}
    public decimal Longitud {get; set;}
    public double RadioMetros {get; set;}
    public int  CantidadEventos {get; set;}
    public int? TipoEventoPredominanteId {get; set;}
    public CatTipoEvento? TipoEventoPredominante {get; set;}
    public bool Activa {get; set;} = true;
}