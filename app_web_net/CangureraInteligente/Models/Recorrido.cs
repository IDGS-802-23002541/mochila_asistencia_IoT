using CangureraInteligente.Models;

public class Recorrido
{
    public int Id {get; set;}
    public int DispositivoId {get; set;}
    public Dispositivo Dispositivo {get; set;} = null!;
    public DateTime FechaInicio {get; set;}
    public DateTime? FechaFin {get; set;}
    public int? Usuario_Edad {get; set;}
    public int? DiscapacidadId {get; set;}
    public CatTipoDiscapacidad? Discapacidad {get; set;}
    public string? Ruta_Coordenadas {get; set;}
    
}