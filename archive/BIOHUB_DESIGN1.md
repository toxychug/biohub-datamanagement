# BioHub · Design Tokens

## Colores
```css
:root {
  --bg: #F0F2F5;
  --surface: #FFFFFF;
  --border: #E2E8F0;
  --text: #1A202C;
  --muted: #718096;
  --brand: #2D8F4E;
  --brand-light: #E8F5ED;
}
```

## Badges
| Badge | BG | Color |
|---|---|---|
| Pendiente | `#FFF7ED` | `#C05621` |
| Aprobado / PUBLIC | `#F0FFF4` | `#276749` |
| RESTRICTED | `#FFF5F5` | `#C53030` |

## Tipografía
- Fuente: **DM Sans** (Google Fonts)
- Headers de columna: `11px`, `600`, uppercase, `letter-spacing: 0.05em`
- Cuerpo tabla: `14px` — nombre científico en `700`, resto en `400`
- Stats: número `28px 700`, label `13px 400`

## Componentes clave

**Fila activa en tabla**
```css
tr.active {
  background: #E8F5ED;
  border-left: 3px solid #2D8F4E;
}
```

**Badge**
```css
.badge {
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}
```

**Botón primario**
```css
.btn {
  background: #2D8F4E;
  color: #fff;
  border-radius: 8px;
  padding: 10px 18px;
}
```

**Tarjetas / paneles**
```css
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  padding: 20px 24px;
}
```

## Panel de detalle
- Aparece debajo de la tabla al seleccionar una fila
- Grid de **3 columnas**: Identificación / Sensibilidad / Aprobación
- Títulos de sección en color `--brand` con ícono inline
