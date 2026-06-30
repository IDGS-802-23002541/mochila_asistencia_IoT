using CangureraInteligente.Models;

public class EventoDetectado
{
    public long Id {get; set;}
    public int RecorridoId {get; set;}
    public Recorrido Recorrido {get; set;} = null!;
    public int TipoEventoId {get; set;}
    public CatTipoEvento TipoEvento {get; set;} = null!;
    public DateTime TimeStampEvento {get; set;}
    public decimal? Latitud {get; set;}
    public decimal? Longitud {get; set;}
    public bool Geo_Es_Estimado {get; set;}
    public decimal? FuerzaImpactoG {get; set;}
    public bool? IrIzquierdo {get; set;}
    public bool? IrDerecho {get; set;}
    public decimal? DistanciaCm {get; set;}

}