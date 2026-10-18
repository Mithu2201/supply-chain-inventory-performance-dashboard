// Example Power Query M. Load one raw CSV with File > Data > Text/CSV, then use Advanced Editor.
// Set pRawOrdersPath via Power Query Parameter (Text) to local data/raw/Orders.csv absolute path.
// Bad dates are turned into null and flagged: original dates must be recovered from a trusted source.
let
  Source = Csv.Document(File.Contents(pRawOrdersPath),[Delimiter=",", Columns=16, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Headers = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
  Trimmed = Table.TransformColumns(Headers, {
      {"OrderStatus", each if _=null then null else Text.Proper(Text.Trim(_)), type nullable text},
      {"Region", each if _=null or Text.Trim(_)="" then "Unknown" else Text.Trim(_), type text}
  }),
  DatesAsText = Table.TransformColumns(Trimmed, {
      {"OrderDate", each try Date.FromText(_) otherwise null, type nullable date},
      {"RequiredDate", each try Date.FromText(_) otherwise null, type nullable date},
      {"ShipDate", each try Date.FromText(_) otherwise null, type nullable date},
      {"DeliveryDate", each try Date.FromText(_) otherwise null, type nullable date}
  }),
  BadDateFlag = Table.AddColumn(DatesAsText,"MissingOrInvalidOrderDate",each [OrderDate]=null,type logical),
  QtyTyped = Table.TransformColumnTypes(BadDateFlag,{
    {"QuantityOrdered",Int64.Type},{"QuantityShipped",Int64.Type},
    {"QuantityBackordered",Int64.Type},{"NetSalesNZD",Currency.Type},
    {"COGSNZD",Currency.Type},{"GrossProfitNZD",Currency.Type}
  })
in
  QtyTyped
