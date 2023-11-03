library(shiny)
library(bslib) # using to customise the appearence of the webpage but is it future proofing instead of using CSS styles. 
#definetaly much easier 



ui <- page_navbar(
  title= 'Ukraine Support Tracker',
  

  
  theme = bs_theme(
    bg = "#ffffff", #A color string for the background.
    fg = "#003c7d", #A color string for the foreground.
    primary = "#de0b0b", #A color to be used for hyperlinks
    secondary = '#c61414',
    base_font = font_google("Roboto"),
    code_font = font_google("Manrope")
    ),
  nav_spacer(),
  nav_panel(title='Dashboard'), 
  nav_panel(title = "Heavy Weapons", 
   p("First page content."),
   mainPanel( # table with heavy weapons 
    dataTableOutput("myTable"),
    
    fluidRow(align="right",
        style = "border-top: 1px solid #b2b2b2;padding: 15px;height:100%; min-height: 110%; background-color: white; color:black; font-family: Sans-serif; font-size:100%; font-weight: bold",
        textOutput("selectedCell")    
      ), 
    fluidRow(align="right",
        style = "border-bottom: 1px solid #b2b2b2;padding: 15px;height:100%; min-height:110%; background-color: white; color:black; font-family: Sans-serif; font-size:100%; font-weight: bold",
        textOutput("selectedCell_delivery")
      ),
      width = 20
      #list(tags$head(tags$style("body {background-color:; }"))),
      #tags$style(HTML('table.dataTable.hover tbody tr:hover, table.dataTable.display tbody tr:hover {background-color: pink !important;}')),
    )
   
   
   ),
  nav_panel(title = "Whatever", 
   p("Second page content.")),
  nav_panel(title = "FAQ", 
    tagList(
    tags$style( #style settings for headers and text 
      "h3{
        text-align:right;
      }"
    )),
  div(style = 'width: 70%;margin:auto', # settings for page container 
  h1('Frequently Asked Questions', align="center"),
  h2('General FAQs', align='center'),
  h3('What data do we collect ?', align='right'),
  p("We track publicly known, bilateral (government to government) commitments on financial, humanitarian, and military aid to Ukraine. We only consider aid going from donor governments into Ukraine and/or helping people within Ukraine. Our data is built on publicly known commitments from government statements, press releases, credible news media, and other official government sources."),
  h3("What data do we not collect?", align='right'),
  h3("What does humanitarian, military, and financial aid mean?"),
  h3("What timeframe do the current and older datasets cover?"),
  h3("Where can I find data on…:"),
  h2("Technical  FAQs", align='right'),
  h3("What is the difference between commitments, deliveries, pledges, appropriations and obligations? "),
  h3("Which countries are being tracking?"),
  h3("Which countries are being tracking?"),
  h3("Which countries are being tracking?"),
  
  p("")
  )
  ),

  nav_menu('D',
   nav_item('D1'),
   nav_item('D2'),
  )





  #nav_spacer(), #used to make a space betwee header and panels 


  #navbar menu styles in CSS (deactivated, just as an example)
# tags$head(tags$style(HTML(
#     '.navbar-static-top {background-color: blue;}', #
#     '.navbar-default .navbar-nav>.active>a {background-color: green;}',))), #changes the color of the first button
  
)
