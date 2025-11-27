import cleaner
import Conventer
import MyExtractor

### Cambia la url en la que quieres realizar el scrappeo  de informacion  
url = ''

### Tener en cuenta q hay q modificar segun los requerimientos de cada pagina y de la estructura q sigue
MyExtractor.main(url)

### Se realiza solo sin necesidad de modificar las carpetas q hay
Conventer()

### Formato final limpio y listo para su uso en los entrenamientos 
cleaner.main()