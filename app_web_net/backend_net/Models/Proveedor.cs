using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;


namespace CangureraInteligente.Models;

[Table("Proveedores", Schema = "Operativo")]
public class Proveedor
{
    [Key]
    public int IdProveedor { get; set; }

    [Required]
    [StringLength(100)]
    public string Nombre { get; set; } = string.Empty;

    [StringLength(20)]
    public string? Telefono { get; set; }

    [StringLength(100)]
    public string? Correo { get; set; }

    [StringLength(200)]
    public string? Direccion { get; set; }

    public bool Activo { get; set; } = true;
    public ICollection<MateriaPrima> MateriasPrimas { get; set; }

}