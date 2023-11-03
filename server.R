library(shiny)
library(DT)
library(htmlwidgets)
library(htmltools)
library(dplyr)
library(gfonts)

server <- function(input, output) {
  
  # load data frame
  data <- read.csv("heavy_per_country.csv")
  
  #sketch 
  header_style <- "@import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap'); #import font
  text-align: center; font-family: Roboto, sans-serif; text-align: center" #style works for top-headers (country, 155mm howitzers, MLRS, Tanks etc.)
  header_style_sub <- "text-align: center; font-family: Helvetica; font-weight: bold"
  footer_style <- "text-align: center; font-family: Roboto, sans-serif;"
  sketch <- htmltools::withTags(table(
    thead(
      tr(
        th(rowspan = 1, '', style = header_style), #hidden
        th(rowspan = 1, 'COUNTRIES', style = header_style),
        th(rowspan = 2, 'COUNTRIES', style = header_style),
        th(colspan = 2, 'ARTILLERY', style = header_style),
        th(colspan = 2,'MLRS', style = header_style),
        th(colspan = 2,'TANKS', style = header_style),
        th(colspan = 2,'AIR DEFENCE', style = header_style),
        th(colspan = 2,'ARMOURED VEHICLES', style = header_style)
        
      ),
      tr(
        lapply((c('Countries', '155mm/152mm Howitzers' )), th), 
        lapply(c('Committed', 'Delivered'), th, style = header_style_sub),
        lapply(c('Committed', 'Delivered'), th),
        lapply(c('Committed', 'Delivered'), th),
        lapply(c('Committed', 'Delivered'), th),
        lapply(c('Committed', 'Delivered'), th),
        lapply(c('howitzers_list',	'mlrs_list'), th),
        lapply(c('tanks_list',	'air_list'), th),
        lapply(c('ifv_list'), th)
      )
    ),
    tfoot( #without dt-center class, footers shift to the left
      th(class = 'dt-center',rowspan = 0, ''), #hidden
      th(class = 'dt-center',rowspan = 0, ''), #hidden
      th(class = 'dt-left',rowspan = 1, 'Total'),
      th(class = 'dt-center', colspan = 1, 'how_com', style = footer_style),
      th(class = 'dt-center', colspan = 1,'how_del', style = footer_style),
      th(class = 'dt-center', colspan = 1,'mlrs_com', footer_style),
      th(class = 'dt-center', colspan = 1,'mlrs_del', footer_style),
      th(class = 'dt-center', colspan = 1,'tanks_com', footer_style),
      th(class = 'dt-center', colspan = 1, 'tanks_del', footer_style),
      th(class = 'dt-center', colspan = 1,'air_com', footer_style),
      th(class = 'dt-center', colspan = 1,'air_del', footer_style),
      th(class = 'dt-center', colspan = 1,'ifv_com', footer_style),
      th(class = 'dt-center', colspan = 1,'ifv_del', footer_style),
      th(class = 'dt-center', colspan = 1,'how_list', footer_style),
      th(class = 'dt-center', colspan = 1,'how_list_del', footer_style),
      th(class = 'dt-center', colspan = 1,'mlrs_list', footer_style),
      th(class = 'dt-center', colspan = 1,'mlrs_list_del', footer_style),
      th(class = 'dt-center', colspan = 1,'tanks_list', footer_style),
      th(class = 'dt-center', colspan = 1,'tanks_list_del', footer_style),
      th(class = 'dt-center', colspan = 1,'air_list', footer_style),
      th(class = 'dt-center', colspan = 1,'air_list_del', footer_style),
      th(class = 'dt-center', colspan = 1,'ifv_list', footer_style),
      th(class = 'dt-center', colspan = 1,'ifv_list_del', footer_style),
      th(class = 'dt-center', colspan = 1,'code', footer_style)
    )
    
    #tableFooter(c('','','Total','','','','','','','','','','','','','','',''))
  ))
  
  
  
  #totals for columns, $(api.column(n) where to place totals, 
  #toFixed - decimals after .
  #first line calculates totals for committed, second calculates for deliveries, third displays it 
  
  jsCode <- "function(row, data, start, end, display) {
  var api = this.api(), data;

  total_com_how = api.column(3, {page: 'current'}).data().reduce( function(a, b) { return a + 
b}, 0);
  total_del_how = api.column(4, {page: 'current'}).data().reduce( function(a, b) { return a + 
b}, 0);
  $( api.column(3).footer() ).html(total_com_how) ;
  $( api.column(4).footer() ).html(total_del_how + ' (' 
  + (total_del_how/total_com_how*100).toFixed(0) +'%)') 
  
    total_com_mlr = api.column(5, {page: 'current'}).data().reduce( function(a, b) { return a + 
b}, 0);
  total_del_mlr = api.column(6, {page: 'current'}).data().reduce( function(a, b) { return a + 
b}, 0);
  $( api.column(5).footer() ).html(total_com_mlr) ;
  $( api.column(6).footer() ).html(total_del_mlr + ' (' 
  + (total_del_how/total_com_how*100).toFixed(0) +'%)')
  
      total_com_mbt = api.column(7, {page: 'current'}).data().reduce( function(a, b) { return a + 
b}, 0);
  total_del_mbt = api.column(8, {page: 'current'}).data().reduce( function(a, b) { return a + 
b}, 0);
  $( api.column(7).footer() ).html(total_com_mbt) ;
  $( api.column(8).footer() ).html(total_del_mbt + ' (' 
  + (total_del_how/total_com_how*100).toFixed(0) +'%)')
  
  total_com_air = api.column(9, {page: 'current'}).data().reduce( function(a, b) { return a + 
b}, 0);
  total_del_air = api.column(10, {page: 'current'}).data().reduce( function(a, b) { return a + 
b}, 0);
  $( api.column(9).footer() ).html(total_com_air) ;
  $( api.column(10).footer() ).html(total_del_air + ' (' 
  + (total_del_how/total_com_how*100).toFixed(0) +'%)') ;
  
  total_com_ifv = api.column(11, {page: 'current'}).data().reduce( function(a, b) { return a + 
b}, 0);
  total_del_ifv = api.column(12, {page: 'current'}).data().reduce( function(a, b) { return a + 
b}, 0);
  $( api.column(11).footer() ).html(total_com_ifv) ;
  $( api.column(12).footer() ).html(total_del_ifv + ' (' 
  + (total_del_how/total_com_how*100).toFixed(0) +'%)')
  
  
  
  
  }"
  
  
  
  
  
  
  for (i in 1:nrow(data)) { 
    data[i,2] <- paste0('<img src="https://cdn.rawgit.com/lipis/flag-icon-css/master/flags/4x3/',
                        data[i,23],'.svg"', 'height="12"></img> ', data[i,2])
  }
  # Render the interactive table
  
  output$myTable <- DT::renderDataTable(datatable(data, #start rendering the table
                                                  #selection = list(mode = 'single', target = 'cell'),
                                                  #style = 'bootstrap',
                                                  #style = "font-size: 75%; width: 75%", #does not work
                                                  class = 'order-column compact',
                                                  extensions = c("FixedColumns", 'Buttons'),
                                                  editable = FALSE,
                                                  escape = FALSE,
                                                  container = sketch,
                                                  selection = list(mode = 'single', target = 'cell'),
                                                  colnames = c('','Countries',	'155mm/152mm Howitzers',	'Multiple Rocket Launchers',	
                                                               'Main Battle Tanks',	'Air Defence',	'Fighting Vehicles (IFV)',	
                                                               'howitzers_list',	'mlrs_list',	'tanks_list',	'air_list',	
                                                               'ifv_list', 'howitzers_delivered','mlrs_delivered',
                                                               'tanks_delivered','air_delivered','ifv_delivered', 'code'),
                                                  options = list(paging = FALSE,
                                                                 fixedHeader = TRUE,
                                                                 pageLength = 20,
                                                                 list(dom = 'Bfrtip', buttons = I('colvis')),
                                                                 fixedColumns = list(leftColumns = 1),
                                                                 order = list(list(3,'desc')), #change order
                                                                 scrollX = FALSE,
                                                                 scrollY = FALSE,
                                                                 autoWidth = FALSE,
                                                                 searching=FALSE,
                                                                 bInfo = FALSE, ## remove information regarding the amount of entries shown
                                                                 columnDefs = list(list(targets = 2, className = 'dt-body-left'), #left align 1 column 
                                                                                   list(targets = 3:12, className = 'dt-body-center'), #center columns
                                                                                   list(targets = '_all',className = 'dt-header-center'), # center the headers
                                                                                   list(targets = c(0,1,13,14,15,16,17,18,19,20,21,22,23), visible = FALSE),
                                                                                   list(width ='100%', targets = 2),
                                                                                   list(width = '50%', targets = 3:12)),
                                                                 #also changes the properties of the columns (switched off because $('') does not have 'body' or 'footer') 
                                                                 
                                                                 initComplete = JS("function(settings, json) {$(this.api().table().body()).css({'font-family': 'sans-serif'})}"),
                                                                 
                                                                 #initComplete = JS(
                                                                 #  "function(settings, json) {",
                                                                 #  "$('').css({'font-family': 'Algeria', 'font-size': '16px', 'font-weight': 'light'});",
                                                                 #  "}"),
                                                                 footerCallback = JS(jsCode)
                                                  )
  ) %>% # CHANGE THE PROPERTIES OF THE COLUMN uncomment in case we want to aplly different font for each column
    formatStyle(3, target= 'row', border = '1px solid black')
  ) 
  
  # Display the selected cell's position
  output$selectedCell <- renderText({
    info <- input$myTable_cell_clicked
    row <- info$row
    col <- info$col
    
    if (!is.null(row) && !is.null(col)) {
      
      if (col == 2) {message <- "Select anouther cell"}
      if (col == 3) {message <- paste0(data[row,13])}
      if (col == 4) {message <- paste0(data[row,14])}
      if (col == 5) {message <- paste0(data[row,15])}
      if (col == 6) {message <- paste0(data[row,16])}
      if (col == 7) {message <- paste0(data[row,17])}
      if (col == 8) {message <- paste0(data[row,18])}
      if (col == 9) {message <- paste0(data[row,19])}
      if (col == 10) {message <- paste0(data[row,20])}
      if (col == 11) {message <- paste0(data[row,21])}
      if (col == 12) {message <- paste0(data[row,22])}
      if (col == 13) {message <- paste0(data[row,23])}
      if (col == 1) {message <- paste0("Selected Cell: Row ", row, ", Column ", col)}
      message
    } else {
      message <- "Select a cell"
      message
    }
    
    
  })
  
  #delivery data
  output$selectedCell_delivery <- renderText({
    info <- input$myTable_cell_clicked
    row <- info$row
    col <- info$col
    
    if (!is.null(row) && !is.null(col)) {
      
      if (col == 2) {message <- " "}
      
      #set delivery field to empty if rows with 0 is clicked
      
      if (data[row,2]==0) {message <-'No deliveries'}
      if (data[row,3]==0) {message <-'No deliveries'}
      if (data[row,4]==0) {message <-'No deliveries'}
      if (data[row,5]==0) {message <-'No deliveries'}
      if (data[row,6]==0) {message <-'No deliveries'}
      if (data[row,7]==0) {message <-'No deliveries'}
      if (data[row,8]==0) {message <-'No deliveries'}
      if (data[row,9]==0) {message <-'No deliveries'}
      if (data[row,10]==0) {message <-'No deliveries'}
      if (data[row,11]==0) {message <-'No deliveries'}
      if (data[row,12]==0) {message <-'No deliveries'}
      
      
      #give a particular number
      
      if (col == 3 & data[row,3]!=0) {message <- paste0(data[row,4], ' out of ', data[row,3], ' delivered (', 
                                                        round((data[row,4]/data[row,3])*100,0),'% delivery rate)')}
      if (col == 4 & data[row,4]!=0) {message <- paste0(data[row,4], ' out of ', data[row,3], ' delivered (', 
                                                        round((data[row,4]/data[row,3])*100,0),'% delivery rate)')}
      if (col == 5 & data[row,5]!=0) {message <- paste0(data[row,6], ' out of ', data[row,5], ' delivered (', 
                                                        round((data[row,6]/data[row,5])*100,0),'% delivery rate)')}
      if (col == 6 & data[row,6]!=0) {message <- paste0(data[row,6], ' out of ', data[row,5], ' delivered (', 
                                                        round((data[row,6]/data[row,5])*100,0),'% delivery rate)')}
      if (col == 7 & data[row,7]!=0) {message <- paste0(data[row,8], ' out of ', data[row,7], ' delivered (', 
                                                        round((data[row,8]/data[row,7])*100,0),'% delivery rate)')}
      if (col == 8 & data[row,8]!=0) {message <- paste0(data[row,8], ' out of ', data[row,7], ' delivered (', 
                                                        round((data[row,8]/data[row,7])*100,0),'% delivery rate)')}
      if (col == 9 & data[row,9]!=0) {message <- paste0(data[row,10], ' out of ', data[row,9], ' delivered (', 
                                                        round((data[row,10]/data[row,9])*100,0),'% delivery rate)')}
      if (col == 10 & data[row,10]!=0) {message <- paste0(data[row,10], ' out of ', data[row,9], ' delivered (', 
                                                          round((data[row,10]/data[row,9])*100,0),'% delivery rate)')}
      if (col == 11 & data[row,11]!=0) {message <- paste0(data[row,12], ' out of ', data[row,11], ' delivered (', 
                                                          round((data[row,12]/data[row,11])*100,0),'% delivery rate)')}
      if (col == 12 & data[row,12]!=0) {message <- paste0(data[row,12], ' out of ', data[row,11], ' delivered (', 
                                                          round((data[row,12]/data[row,11])*100,0),'% delivery rate)')}
      
      
      message
    } else {
      message <- "No deliveries"
      message
    }
    
    
  })
}