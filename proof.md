# Unidad 4. Servicios web

## Introducción

Los servicios web constituyen una tecnología fundamental para la comunicación entre aplicaciones en entornos distribuidos. Su propósito principal es permitir que diferentes sistemas intercambien información y utilicen funcionalidades de manera remota mediante protocolos, formatos y estándares comunes. En el desarrollo de software actual, los servicios web son esenciales para integrar aplicaciones empresariales, plataformas móviles, sistemas en la nube y arquitecturas basadas en microservicios. Su evolución ha pasado por enfoques formales como SOAP, estilos arquitectónicos como REST y modelos de consulta flexibles como GraphQL.

## 4.1. Definición y características

Un servicio web puede definirse como un componente de software que permite la comunicación entre aplicaciones a través de una red, generalmente mediante Internet. Su función consiste en exponer datos, operaciones o funcionalidades para que otros sistemas puedan consumirlos sin necesidad de conocer los detalles internos de su implementación. En este sentido, un servicio web funciona como una interfaz entre un cliente, que realiza solicitudes, y un servidor, que procesa dichas solicitudes y devuelve una respuesta.

Una de las características principales de los servicios web es la interoperabilidad, ya que permiten que sistemas desarrollados con diferentes lenguajes de programación, plataformas o tecnologías puedan comunicarse mediante estándares comunes. Esta capacidad resulta especialmente importante en organizaciones donde conviven múltiples sistemas informáticos. Además, los servicios web favorecen la reutilización, debido a que una misma funcionalidad puede ser consumida por varias aplicaciones, lo que reduce la duplicación de código y facilita el mantenimiento.

Otra característica relevante es la modularidad. Los servicios web permiten dividir un sistema complejo en componentes independientes que se comunican mediante interfaces bien definidas. Esta organización facilita el desarrollo, la actualización y la integración de nuevas funcionalidades. Asimismo, pueden ser escalables cuando se diseñan adecuadamente, ya que permiten atender un número creciente de solicitudes mediante infraestructuras distribuidas o servicios en la nube.

En términos técnicos, los servicios web suelen emplear protocolos como HTTP o HTTPS y formatos de intercambio de datos como XML o JSON. La elección de estos elementos depende del tipo de arquitectura implementada, de los requisitos del sistema y del contexto de uso. HTTP, por ejemplo, define métodos de solicitud que permiten estructurar la interacción entre clientes y servidores en la Web (Fielding et al., 2022).

## 4.2. Antecedente

El surgimiento de los servicios web se relaciona con la necesidad de integrar sistemas distribuidos y heterogéneos. Antes de su consolidación, muchas organizaciones dependían de soluciones propietarias o mecanismos internos para conectar aplicaciones, lo que generaba problemas de compatibilidad, dependencia tecnológica y costos elevados de mantenimiento.

Con el crecimiento de Internet y de los sistemas empresariales distribuidos, se hizo necesario establecer mecanismos estandarizados para el intercambio de información entre aplicaciones remotas. En este contexto, los servicios web aparecieron como una solución orientada a facilitar la comunicación entre sistemas mediante protocolos abiertos y formatos estructurados.

En sus primeras etapas, los servicios web estuvieron estrechamente relacionados con XML, debido a que este lenguaje permitía representar datos de forma estructurada y comprensible para distintos sistemas. A partir de esta base surgieron tecnologías formales para el intercambio de mensajes, entre las cuales destacó SOAP. Este enfoque permitió establecer contratos de comunicación, describir operaciones y definir estructuras de mensajes para la interacción entre aplicaciones distribuidas.

Los antecedentes de los servicios web muestran una evolución desde modelos rígidos y altamente estructurados hacia alternativas más ligeras y flexibles. Esta transformación fue impulsada por las nuevas necesidades del desarrollo web, el crecimiento de las aplicaciones móviles, la expansión de la computación en la nube y la demanda de interfaces más eficientes para el intercambio de datos.

### 4.2.1. SOAP

SOAP, siglas de *Simple Object Access Protocol*, es un protocolo de mensajería utilizado para el intercambio de información estructurada en entornos descentralizados y distribuidos. La especificación de SOAP 1.2 lo describe como un marco extensible de mensajería basado en tecnologías XML, diseñado para intercambiar mensajes sobre distintos protocolos subyacentes (W3C, 2007).

Un mensaje SOAP suele estar compuesto por una envoltura o *envelope*, un encabezado opcional y un cuerpo. La envoltura delimita el mensaje; el encabezado puede incluir información adicional, como datos de seguridad o control; y el cuerpo contiene la solicitud o respuesta correspondiente a una operación específica. Esta estructura permite que los mensajes sean procesados de manera uniforme por diferentes sistemas.

SOAP suele asociarse con WSDL, *Web Services Description Language*, que permite describir formalmente las operaciones disponibles en un servicio web, los parámetros requeridos y los tipos de datos utilizados. Esta característica convierte a SOAP en una opción adecuada para entornos donde se requieren contratos estrictos, documentación precisa y reglas claras de comunicación.

Durante varios años, SOAP fue ampliamente utilizado en sistemas empresariales, especialmente en sectores donde la seguridad, la confiabilidad y la formalidad de los contratos de servicio eran aspectos fundamentales. Sin embargo, SOAP también presenta limitaciones. El uso de XML puede generar mensajes extensos y menos eficientes en comparación con formatos más ligeros como JSON. Además, su implementación puede resultar más compleja que la de enfoques actuales como REST. Por ello, aunque SOAP continúa siendo útil en determinados contextos empresariales, muchas aplicaciones modernas han adoptado alternativas más simples y flexibles.

## 4.3. Presente

En la actualidad, los servicios web son un componente esencial del desarrollo de software. La expansión de aplicaciones móviles, plataformas web, sistemas en la nube y arquitecturas de microservicios ha impulsado el uso de mecanismos de comunicación más ligeros, flexibles y eficientes. En este contexto, REST y GraphQL se han convertido en dos enfoques ampliamente utilizados para el diseño de interfaces de programación de aplicaciones, conocidas como API.

El presente de los servicios web se caracteriza por la necesidad de ofrecer respuestas rápidas, estructuras de datos claras, facilidad de integración, seguridad y compatibilidad con múltiples clientes. Una misma API puede ser consumida por aplicaciones web, dispositivos móviles, sistemas internos de una organización o servicios externos. Por esta razón, el diseño de servicios web debe considerar aspectos como rendimiento, escalabilidad, documentación, autenticación y mantenimiento.

REST se ha consolidado como una arquitectura popular debido a su simplicidad y a su relación directa con HTTP. GraphQL, por su parte, ha ganado relevancia porque permite a los clientes solicitar únicamente los datos que necesitan mediante un esquema tipado y consultas estructuradas (GraphQL Foundation, 2026a).

### 4.3.1. REST

REST, siglas de *Representational State Transfer*, es un estilo arquitectónico utilizado para diseñar sistemas distribuidos basados en recursos. Fue propuesto por Roy Fielding en su tesis doctoral sobre estilos arquitectónicos y diseño de arquitecturas de software basadas en red (Fielding, 2000).

A diferencia de SOAP, REST no es un protocolo, sino un conjunto de restricciones arquitectónicas. Su funcionamiento se basa en recursos, los cuales son identificados mediante direcciones URL y manipulados a través de métodos HTTP. En una arquitectura REST, cada recurso representa una entidad del sistema, como usuarios, productos, pedidos, documentos o publicaciones.

Para interactuar con estos recursos se emplean métodos HTTP. El método GET se utiliza comúnmente para consultar información; POST, para enviar datos o crear recursos; PUT, para reemplazar o actualizar recursos; PATCH, para realizar modificaciones parciales; y DELETE, para eliminar recursos. La especificación HTTP Semantics define los métodos y la semántica general del protocolo HTTP, incluyendo su carácter de protocolo de aplicación sin estado (*stateless*) (Fielding et al., 2022).

Una de las principales ventajas de REST es su simplicidad. Al apoyarse en HTTP, resulta familiar para los desarrolladores web y puede integrarse fácilmente con navegadores, aplicaciones móviles y sistemas externos. Además, REST suele utilizar JSON como formato de intercambio de datos, lo que permite mensajes más ligeros y fáciles de procesar que aquellos basados en XML.

REST también favorece la escalabilidad, especialmente cuando se aplica el principio de ausencia de estado. Esto significa que cada solicitud enviada por el cliente debe contener toda la información necesaria para que el servidor pueda procesarla, sin depender de una sesión almacenada previamente. Esta característica facilita la distribución de solicitudes entre múltiples servidores y mejora la capacidad de crecimiento del sistema.

No obstante, REST puede presentar algunos desafíos en aplicaciones complejas. En determinados casos, el cliente necesita realizar varias solicitudes para obtener todos los datos requeridos. En otros, puede recibir más información de la necesaria. Estos problemas suelen conocerse como *underfetching* y *overfetching*, respectivamente, y han motivado la adopción de alternativas como GraphQL en proyectos que requieren mayor flexibilidad en la consulta de datos.

### 4.3.2. GraphQL

GraphQL es un lenguaje de consulta para API y un entorno de ejecución del lado del servidor. Su propósito es permitir que los clientes soliciten exactamente los datos que necesitan, evitando recibir información innecesaria. De acuerdo con su documentación oficial, GraphQL utiliza un esquema fuertemente tipado para definir las relaciones entre los datos y hacer que las API sean más flexibles y predecibles (GraphQL Foundation, 2026a).

A diferencia de REST, donde la estructura de las respuestas suele estar definida por endpoints específicos, GraphQL permite que el cliente determine la forma y el contenido de la respuesta mediante consultas estructuradas. Una característica central de GraphQL es que normalmente opera mediante un único endpoint, desde el cual el cliente puede realizar operaciones para consultar o modificar datos.

GraphQL se basa en un esquema que define los tipos de datos disponibles, sus relaciones y las operaciones permitidas. Este esquema funciona como una descripción formal de las capacidades de la API. La documentación oficial señala que el sistema de tipos de GraphQL describe qué datos pueden ser consultados y permite a los clientes enviar consultas que devuelven resultados predecibles (GraphQL Foundation, 2026b).

Entre sus ventajas se encuentra la flexibilidad en el consumo de datos. El cliente puede solicitar únicamente los campos que necesita, lo que puede reducir la transferencia de información innecesaria. Sin embargo, GraphQL también requiere una planificación cuidadosa, ya que consultas demasiado complejas pueden afectar el rendimiento del servidor. Por esta razón, es necesario implementar controles de seguridad, límites de consulta, autenticación, autorización, manejo de errores y estrategias de optimización.

#### 4.3.2.1. Query

Una *query* en GraphQL es una operación utilizada para solicitar datos al servidor. Su propósito principal es realizar consultas de lectura, es decir, obtener información sin modificar el estado del sistema. A través de una query, el cliente define los campos específicos que desea recibir y la estructura de la respuesta esperada.

Por ejemplo, en una aplicación académica, una query podría solicitar únicamente el nombre de un estudiante, su matrícula y las asignaturas inscritas, sin recuperar todos los datos almacenados sobre dicho estudiante. Esta capacidad de selección precisa permite optimizar la comunicación entre cliente y servidor, ya que reduce el envío de información innecesaria.

Las queries dependen del esquema definido por el servidor. Esto significa que el cliente solo puede solicitar campos, tipos y relaciones previamente declarados. Si una consulta no coincide con dicho esquema, puede ser rechazada antes de ejecutarse. La documentación oficial de GraphQL explica que las operaciones de consulta permiten leer datos desde un servidor GraphQL de forma estructurada (GraphQL Foundation, 2026c).

#### 4.3.2.2. Mutation

Una *mutation* en GraphQL es una operación destinada a modificar datos en el servidor. Mientras que las queries se utilizan para consultar información, las mutations se emplean para crear, actualizar o eliminar registros. Por lo tanto, representan operaciones que cambian el estado del sistema.

Una mutation puede utilizarse para registrar un nuevo usuario, actualizar los datos de un producto, modificar la información de una cuenta o eliminar un registro de una base de datos. Al igual que las queries, las mutations permiten especificar qué información debe devolverse después de ejecutar la operación. Esto permite que el cliente reciba los datos actualizados sin necesidad de realizar una solicitud adicional.

El diseño de mutations requiere especial atención a la seguridad y a la integridad de los datos. Es necesario validar la información recibida, verificar los permisos del usuario y controlar posibles errores durante la ejecución. GraphQL define las mutations como operaciones orientadas a escribir datos y producir cambios a través del esquema de la API (GraphQL Foundation, 2026d).

#### 4.3.2.3. Client

El cliente en GraphQL es la parte de la aplicación que consume la API mediante queries y mutations. Puede tratarse de una aplicación web, una aplicación móvil, un sistema de escritorio o incluso otro servicio que necesite interactuar con el servidor. Su función consiste en construir las solicitudes, enviarlas al endpoint GraphQL y procesar las respuestas recibidas.

En GraphQL, el cliente tiene un papel activo porque puede especificar con precisión los datos que necesita. Esta característica permite adaptar las solicitudes a los requerimientos de cada vista o funcionalidad de la aplicación. Como resultado, se puede mejorar la eficiencia en el consumo de datos y reducir el tráfico innecesario entre cliente y servidor.

En el desarrollo moderno existen bibliotecas especializadas que facilitan la implementación de clientes GraphQL. Estas herramientas pueden ayudar a gestionar consultas, almacenar datos en caché, actualizar interfaces de usuario y manejar estados de carga o error. No obstante, su uso también implica responsabilidades, ya que los desarrolladores deben conocer el esquema de la API y diseñar consultas eficientes para evitar sobrecargar el servidor.

## 4.4. Desarrollo de un proyecto con servicio web

El desarrollo de un proyecto con servicio web requiere una planificación ordenada que considere tanto los aspectos funcionales como los técnicos. El primer paso consiste en identificar el problema que se desea resolver y definir los requisitos del sistema. Esto incluye determinar qué datos serán gestionados, qué operaciones estarán disponibles, qué usuarios interactuarán con el servicio y qué restricciones técnicas deben tomarse en cuenta.

Después de establecer los requisitos, se debe seleccionar la arquitectura más adecuada. Si el proyecto requiere una solución sencilla, ampliamente compatible y basada en recursos, REST puede ser una opción apropiada. Si se necesita mayor flexibilidad en la consulta de datos, especialmente en aplicaciones con interfaces complejas, GraphQL puede resultar conveniente. En contextos empresariales donde se requieren contratos estrictos o integración con sistemas heredados, SOAP puede continuar siendo una alternativa válida.

Una vez definida la arquitectura, se diseña la API. En REST, esto implica establecer los recursos, las URL, los métodos HTTP y los códigos de estado correspondientes. En GraphQL, se diseña el esquema, los tipos de datos, las queries y las mutations. En SOAP, se definen las operaciones, los mensajes XML y el contrato WSDL. En todos los casos, el diseño debe ser claro, coherente y fácil de comprender para facilitar el consumo y mantenimiento del servicio.

La implementación del proyecto incluye la programación de la lógica del servidor, la conexión con bases de datos, la validación de datos, la autenticación de usuarios, la autorización de operaciones y el manejo de errores. También es necesario aplicar buenas prácticas de seguridad, como el uso de HTTPS, la validación de entradas, el control de acceso y la protección contra solicitudes maliciosas.

Posteriormente, se deben realizar pruebas para verificar el funcionamiento del servicio. Estas pruebas pueden incluir pruebas unitarias, pruebas de integración y pruebas funcionales. Su objetivo es comprobar que las operaciones respondan correctamente y que los datos se procesen de forma adecuada. Además, la documentación del servicio es fundamental, ya que permite que otros desarrolladores comprendan cómo utilizar la API.

Finalmente, el servicio web debe desplegarse en un entorno de ejecución, como un servidor institucional, una infraestructura local o una plataforma en la nube. Después del despliegue, es necesario monitorear su rendimiento, registrar errores y aplicar actualizaciones cuando sea necesario. Un servicio web no debe considerarse un producto estático, sino un componente que requiere mantenimiento, mejora continua y adaptación a nuevas necesidades.

## Referencias

Fielding, R. T. (2000). *Architectural styles and the design of network-based software architectures* [Doctoral dissertation, University of California, Irvine]. :contentReference[oaicite:0]{index=0}

Fielding, R., Nottingham, M., & Reschke, J. (2022). *HTTP semantics* (RFC 9110). Internet Engineering Task Force. :contentReference[oaicite:1]{index=1}

GraphQL Foundation. (2026a). *GraphQL: The query language for modern APIs*. :contentReference[oaicite:2]{index=2}

GraphQL Foundation. (2026b). *Schemas and types*. :contentReference[oaicite:3]{index=3}

GraphQL Foundation. (2026c). *Queries*. :contentReference[oaicite:4]{index=4}

GraphQL Foundation. (2026d). *Mutations*. :contentReference[oaicite:5]{index=5}

World Wide Web Consortium. (2007). *SOAP version 1.2 part 1: Messaging framework* (2nd ed.). :contentReference[oaicite:6]{index=6}