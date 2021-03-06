import os

import pandas as pd
import tqdm

from get_taxa import getScientificNameId
from get_taxa import get_gbif_synonyms
from get_taxa import get_taxonomy
import urllib.parse

pd.options.mode.chained_assignment = None  # default='warn'

taxa = {
    'Populus canescens', 'Eriophyes similis', 'Calocybe gangraenosa', 'Lecanora achariana',
    'Cortinarius diasemospermus', 'Carex dacica', 'Curculio marmoratus', 'Anomalon anae', 'Naohidemyces vaccinii',
    'Erirhinus aethiops', 'Stenophylax lateralis', 'Anthropoides virgo', 'Pachyella celtica', 'Cyathicula cyathoidea',
    'Laburnum watereri', 'Piloderma bicolor', 'Conioselinum tataricum', 'Panzeria truncata', 'Matricaria discoidea',
    'Xanthoparmelia delisei', 'Polytrichastrum formosum', 'Solanum lycopersicum', 'Cantharis coccinea',
    'Agrilinus ater', 'Plicaturopsis crispa', 'Lathridius nodifer', 'Hypopitys monotropa', 'Corixa dorsalis',
    'Entoloma fulvoviolaceum', 'Satchelliella mutua', 'Tilia vulgaris', 'Orthotrichum affine', 'Leccinum holopus',
    'Bohemanella frigida', 'Flavoscypha cantharella', 'Speyeria aglaia', 'Hemimycena hirsuta', 'Lachnum corticale',
    'Lepidoderma trevelyanii', 'Reynoutria bohemica', 'Echinostelium cribrarioides', 'Acer tataricum',
    'Pycnogonum litorale', 'Tenthredo mesomelas', 'Tremella encephala', 'Psila hennigi', 'Clitocybe costata',
    'Lanius meridionalis', 'Cyclocybe erebia', 'Evacanthus interrupta', 'Bryum capillare', 'Pilularia globulifera',
    'Anas penelope x platyrhynchos', 'Gelatoporia dichroa', 'Solanum angustifolium', 'Tephrocybe rancida',
    'Sylvia crassirostris', 'Papaver nudicaule', 'Parmelia serrana', 'Phylloscopus trochilus x collybita',
    'Melanocorypha leucoptera', 'Dasypoda altercator', 'Crombrugghia tristis', 'Bryum alpinum', 'Bryum moravicum',
    'Eriophyes sorbi', 'Cornus suecica', 'Platycheirus dexter', 'Sagaranella tylicolor', 'Zoothera dauma',
    'Caloplaca ferruginea', 'Xanthoria polycarpa', 'Lophozia sudetica', 'Astilbe chinensis x japonica x rosea',
    'Hyphodontia cineracea', 'Logfia arvensis', 'Poa tolmatchewii', 'Toninia sedifolia', 'Polygonatum hybridum',
    'Lauxania pulchra', 'Collema occultatum', 'Sceptridium multifidum', 'Spiraea vanhouttei', 'Lycopodium lagopus',
    'Psila bicolor', 'Magdalis violacea', 'Koenigia polystachya', 'Cheilosia tarditas', 'Steromphala cineraria',
    'Aphodius coniugatus', 'Sarcodon versipellis', 'Araneus thaddeus', 'Cornus sanguinea', 'Cymatia bonsdorffi',
    'Peziza queletii', 'Beta maritima', 'Mycopan scabripes', 'Adelges abietis', 'Caloplaca holocarpa',
    'Sarcodon joeides', 'Kurtia argillacea', 'Machimus atricapillus', 'Odonticium flabelliradiatum',
    'Pteridium latiusculum', 'Tipula signata', 'Carex utriculata', 'Amblystegium subtile', 'Reticularia olivacea',
    'Anomoia purmunda', 'Erigeron canadensis', 'Contacyphon coarctatus', 'Atriplex nudicaulis', 'Opegrapha gyrocarpa',
    'Sorbus austriaca', 'Suillellus queletii', 'Leucoscypha alpestris', 'Anguliphantes karpinskii',
    'Cabalodontia subcretacea', 'Erastia salmonicolor', 'Pentanema salicinum', 'Apus melba', 'Parasemia plantaginis',
    'Dactylorhiza lapponica', 'Saxifraga flagellaris', 'Conocybe rugosa', 'Dactylorhiza viridis', 'Onesia viarum',
    'Caloplaca scopularis', 'Xeromphalina picta', 'Larus argentatus x hyperboreus', 'Larus atricilla',
    'Centaurea cyanus', 'Melanelia sorediata', 'Phaenops cyanea', 'Scaeva melanostoma', 'Speudotettix subfuscula',
    'Spinulum annotinum', 'Sylvia nana', 'Phellinus pomaceus', 'Pholiota pinicola', 'Rhodaphodius foetens',
    'Nicotiana alata x forgetiana', 'Acalitus longisetosus', 'Nigrograna fuscidula', 'Collema cristatum',
    'Collema fuscovirens', 'Spirontocaris lilljeborgii', 'Smidtia conspersa', 'Agoliinus nemoralis',
    'Cantharellus cinereus', 'Capella media', 'Thyronectria coryli', 'Stenophylax sequax', 'Malus purpurea',
    'Pellia endiviifolia', 'Acrossus rufipes', 'Junghuhnia collabens', 'Cecidomyia strobilina',
    'Phaeoacremonium minimum', 'Heringocrania unimaculella', 'Xanthoria candelaria', 'Planolinoides borealis',
    'Cheilosia corydon', 'Lysibia nana', 'Adelges viridis', 'Calonectris diomedea', 'Bryum cryophilum',
    'Gremmenia infestans', 'Pontania collectanea', 'Elachista dispilella', 'Pachyphiale fagicola', 'Neckera crispa',
    'Palloptera saltuum', 'Corisa nigrolineata', 'Typhula filiformis', 'Silene coronaria', 'Hyalinia rubella',
    'Aricia eumedon', 'Berberis aquifolium', 'Cortinarius croceocoeruleus', 'Pholiota alnicola', 'Sarea resinae',
    'Clitocybe squamulosa', 'Oligotrophus juniperina', 'Orthotrichum rupestre', 'Silene suecica',
    'Cinclidotus fontinalioides', 'Grus canadensis', 'Trachyspora alchemillae', 'Lachnella sauteri',
    'Pleuroptya ruralis', 'Epichloe typhina', 'Amyloporia sinuosa', 'Botryobasidium vagum', 'Ctenolepisma longicaudata',
    'Eupeodes lapponicus', 'Thinopyrum junceum', 'Epilobium angustifolium', 'Mensularia nodulosa',
    'Cladostephus spongiosus', 'Odonticium septocystidia', 'Sterna nilotica', 'Plantago uniflora', 'Pediculus humanus',
    'Potentilla argyrophylla', 'Sclerophora nivea', 'Flaviporus citrinellus', 'Amanita contui', 'Lanzia luteovirescens',
    'Novafrontina uncata', 'Zostera noltii', 'Brumus quadripustulatus', 'Guepiniopsis alpina', 'Bryum caespiticium',
    'Saxifraga opdalensis', 'Sciasminettia frontalis', 'Bromus benekenii', 'Inocybe glabripes', 'Xanthogramma festiva',
    'Hyphodontia quercina', 'Idiodonus cruentata', 'Blysmus rufus', 'Alboleptonia sericella', 'Orthotrichum lyellii',
    'Draba norvegica', 'Cimex najas', 'Psila atra', 'Teuchestes fossor', 'Limicola falcinellus', 'Lentinus brumalis',
    'Squalius cephalus', 'Polysiphonia fucoides', 'Tolypocladium capitatum', 'Sarcodontia spumea',
    'Puccinia brachypodii', 'Toninia rosulata', 'Rinodina hallii', 'Tenthredo pini', 'Morchella eohespera',
    'Inonotus leporinus', 'Conocybe nemoralis', 'Postia rennyi', 'Petunia atkinsiana', 'Podostroma leucopus',
    'Phylloscopus sibillatrix', 'Typhula fistulosa', 'Phellinopsis conchata', 'Saxifraga osloensis',
    'Calvatia gigantea', 'Quedius fulgidus', 'Epaphius secalis', 'Tyto alba', 'Catoptrophorus semipalmatus',
    'Heliosperma pusillum', 'Drosera obovata', 'Lejops contracta', 'Magallana gigas', 'Collema auriforme',
    'Leptogium lichenoides', 'Neolygus viridis', 'Xanthia icteritia', 'Hygrohypnum smithii', 'Spilichneumon ammonius',
    'Xanthoria elegans', 'Saxifraga urbium', 'Agrochola lota', 'Cortinarius inolens', 'Festuca richardsonii',
    'Xanthoria fallax', 'Phaeostigma notatum', 'Xylodon crustosus', 'Eristalis lineata', 'Lepas fascicularis',
    'Ciboria juncorum', 'Agrochola circellaris', 'Helvella arcto-alpina', 'Opegrapha rufescens',
    'Chrysotoxum fasciatus', 'Geum intermedium', 'Ceraceomyces borealis', 'Compsobata nigricornis', 'Lenzites betulina',
    'Rutstroemia bulgarioides', 'Sporothrix polyporicola', 'Naucoria celluloderma', 'Fuscoporia ferrea',
    'Dysmachus picipes', 'Phloeomana clavata', 'Lycopsis arvensis', 'Narcissus cuneiflorus',
    'Pseudatemelia flavifrontella', 'Sigarispora caulium', 'Phasia barbifrons', 'Crocosmia crocosmiiflora',
    'Lamium galeobdolon', 'Enterion cyaneum', 'Plantago uliginosa', 'Rhynchalastor picticrus',
    'Podosphaera clandestina', 'Centaurea montana', 'Terellia immaculata', 'Xanthocyparis nootkatensis',
    'Rubus parviflorus', 'Laphria gilva', 'Buglossoporus quercinus', 'Rhinanthus alectorolophus', 'Chrysomela elongata',
    'Anthoxanthum monticola', 'Bryum pallescens', 'Naucoria amarescens', 'Rhynchaenus ericae',
    'Pseudatemelia josephinae', 'Pistosia testacea', 'Onopordum acaulon', 'Viola wittrockiana', 'Hippophae rhamnoides',
    'Lactuca muralis', 'Hymenochaetopsis tabacina', 'Hyaloscypha minuta', 'Apterogenum ypsillon',
    'Atheliachaete sanguinea', 'Arthothelium lirellans', 'Nannfeldtiella guldeniae', 'Idiocerus elegans',
    'Sarcodon scabrosus', 'Cherleria biflora', 'Ligusticum scoticum', 'Hieracium dovrense', 'Vespa spinipes',
    'Ditrichum gracile', 'Connopus acervatus', 'Trentepohlia jolithus', 'Pachyphiale carneola', 'Phascum cuspidatum',
    'Tragopogon minor', 'Lactarius omphaliiformis', 'Papaver dubium', 'Neofuscelia loxodes', 'Sagartiogeton viduatus',
    'Micranthes hieracifolia', 'Caloplaca verruculifera', 'Gymnocephalus cernua', 'Aedes communis',
    'Acrossus depressus', 'Isotoma trispinata', 'Helicoma fumosum', 'Salix fragilis', 'Caloplaca biatorina',
    'Uromyces fallens', 'Phellopilus nigrolimitatus', 'Euphrasia vernalis', 'Cerioporus mollis',
    'Closterotomus norvegicus', 'Mentha piperita', 'Ombrophila janthina', 'Melanohalea septentrionalis',
    'Lamyra marginata', 'Anas strepera', 'Pseudocyphellaria crocata', 'Pezizella vulgaris', 'Riccardia chamedryfolia',
    'Melogramma spiniferum', 'Antennaria lanata', 'Plebejus optilete', 'Neofavolus suavissimus', 'Carex salina',
    'Anomodon attenuatus', 'Pipiza festiva', 'Calamagrostis purpurea', 'Chiridopsis bipunctata',
    'Melinopterus sphacelatus', 'Naucoria bohemica', 'Mycena tintinnabulum', 'Trametes trogii',
    'Rhopalodontus perforatus', 'Melinopterus punctatosulcatus', 'Ulota phyllantha', 'Hemimycena epichloe',
    'Conocybe pygmaeoaffinis', 'Pilobolus chrystallinus', 'Bryum rubens', 'Conocybe filipes', 'Pseudoleskea patens',
    'Ischnus alternator', 'Peregriana peregra', 'Xanthoparmelia digitiformis', 'Cabalodontia cretacea',
    'Radulodon aneirinus', 'Agathomyia wankowiczii', 'Hartigia linearis', 'Epistrophe euchromus',
    'Ranunculus propinquus', 'Cortinarius iliopodius', 'Poa jemtlandica', 'Bryum pseudotriquetrum',
    'Evacanthus acuminata', 'Megamelus venosus', 'Saxifraga geum', 'Helictochloa pratensis', 'Argentina anserina',
    'Saxifraga svalbardensis', 'Saxifraga arendsii', 'Orthotrichum gymnostomum', 'Tricholoma lascivum',
    'Dolichovespula silvestris', 'Aureoboletus projectellus', 'Oxytropis campestris', 'Sphaerellopsis filum',
    'Pinus uncinata', 'Xanthoporia radiata', 'Anas sibilatrix', 'Phlebia tremellosa', 'Flavoscypha phlebophora',
    'Leptogium tenuissimum', 'Thyronectria cucurbitula', 'Russula atropurpurea', 'Tolypocladium ophioglossoides',
    'Panzeria rudis', 'Nothorhina punctata', 'Emberiza leucocephalos x citrinella', 'Tyromyces lacteus',
    'Stellaria alsine', 'Racomitrium microcarpum', 'Proutia norvegica', 'Curculio pyrrhoceras', 'Xanthia gilvago',
    'Xylotrechus rusticus', 'Fomitopsis betulina', 'Spilosoma lutea', 'Hieracium schmidtii', 'Calathella eruciformis',
    'Cornus alba', 'Arthothelium ruanum', 'Meiosimyza decempunctata', 'Rhinanthus groenlandicus', 'Bonomyces sinopicus',
    'Ampullaceana balthica', 'Ensis directus', 'Agoliinus lapponum', 'Tripleurospermum hookeri',
    'Borkhausenia intermedia', 'Stroemiellus stroemi', 'Collema undulatum', 'Oxystegus tenuirostris',
    'Melangyna sexguttata', 'Corisa distincta', 'Dactylorhiza fuchsii', 'Aphelia unitana', 'Agrochola macilenta',
    'Rosa dumalis', 'Salix smithiana', 'Arthothelium orbilliferum', 'Elymus macrourus', 'Thelomma ocellatum',
    'Plebejus orbitulus', 'Mordella frontalis', 'Vespa parietum', 'Eriothrix rufomaculatus',
    'Somateria mollissima x spectabilis', 'Platycheirus rosarum', 'Euophrys petrensis', 'Gibbera myrtilli',
    'Vaccinium microcarpum', 'Lophochaeta ignota', 'Phlebia femsjoeensis', 'Scilla siberica', 'Musca citrofasciata',
    'Ips impressa', 'Hypnum imponens', 'Pseudocalliergon turgescens', 'Isotoma notabilis', 'Orthotrichum speciosum',
    'Bromus inermis', 'Symphyotrichum salignum', 'Vesperus luridus', 'Dendrocopos minor', 'Neogalerucella calmariensis',
    'Micropodoiulus scandinavius', 'Picea lutzii', 'Sagartiogeton laceratus', 'Clitopilus geminus',
    'Gobiusculus flavescens', 'Tryngites subruficollis', 'Gymnosoma clavata', 'Bromus sterilis',
    'Compsidolon salicellum', 'Chen rossii', 'Melanelia panniformis', 'Oreoneta frigida', 'Ischnus migrator',
    'Camponotus ligniperdus', 'Vaccinium oxycoccos', 'Primula acaulis', 'Taraxacum erythrospermum',
    'Anthostoma turgidum', 'Alchemilla vulgaris', 'Glischrochilus quadripuncatus', 'Tephrocybe putida',
    'Dermestes clavicornis', 'Arthopyrenia antecellens', 'Hygrocybe ovina', 'Hygrophorus persicolor',
    'Gloiothele citrina', 'Chrysogaster parumplicata', 'Luzula arctica', 'Dicallomera fascelina',
    'Crioceris subspinosa', 'Ditrichum flexicaule', 'Eristalis abusivus', 'Arabidopsis lyrata',
    'Narcissus incomparabilis', 'Festuca altissima', 'Ajuga genevensis', 'Campanula giesekiana', 'Ramularia endophylla',
    'Podoschistus scutellaris', 'Pseudoleskea radicosa', 'Leptogium gelatinosum', 'Equisetum trachyodon',
    'Sarcodon fuligineoviolaceus', 'Silene flos-cuculi', 'Polythrincium trifolii', 'Asplenium alternifolium',
    'Dactylorhiza purpurella', 'Antrodia albida', 'Xylodon sambuci', 'Clitopilus caelatus', 'Hypositticus pubescens',
    'Ichneumon insidiosus', 'Phedimus middendorfianus', 'Mutatoderma mutatum', 'Lecanium corni',
    'Pseudoclitopilus rhodoleucus', 'Cosmoscarta abdominalis', 'Polyxenus lagura', 'Lyda gyllenhali', 'Conocybe vexans',
    'Epilobium latifolium', 'Psila pallida', 'Hypnum callichroum', 'Eutypa flavovirens', 'Byssostilbe stilbigera',
    'Forsythia intermedia', 'Chelidura guentheri', 'Narcissus cyclazetta', 'Cheilosia bardus', 'Sarcodon fennicus',
    'Scilla verna', 'Pycnoporus cinnabarinus', 'Lyophyllum onychinum', 'Saxicola maurus', 'Pseudoleskea incurvata',
    'Lactarius volemus', 'Hypnum bambergeri', 'Lophozia incisa', 'Bodilopsis rufus', 'Coryneum lanciforme',
    'Calobatella petronella', 'Lentinus substrictus', 'Sarcodon glaucopus', 'Cortinarius betuletorum', 'Elymus repens',
    'Sphaerophoria rueppellii', 'Palloptera trimacula', 'Chrysotus laesus', 'Cornus sericea', 'Contacyphon padi',
    'Poterium sanguisorba', 'Arthonia elegans', 'Megalonotus chiragrus', 'Laeticutis cristata',
    'Korscheltellus lupulinus', 'Draba glabella', 'Hyperbatus sternoxanthus', 'Ectoedemia atrifrontella',
    'Brongniartella byssoides', 'Aquila clanga', 'Botryohypochnus isabellinus', 'Melangyna guttata',
    'Attelabus monoceros', 'Anoscopus flavostriata', 'Spiraea billardii', 'Polycephalomyces ramosus',
    'Peltigera retifoveata', 'Tiphia minuta', 'Orthotrichum striatum', 'Scleranthus polycarpos', 'Carex fuliginosa',
    'Phellinidium ferrugineofuscum', 'Postia sericeomollis', 'Dendrocopos leucotos x major', 'Lonicera pileata',
    'Motacilla citreola x  flava', 'Seligeria campylopoda', 'Hydrothassa glabra', 'Koenigia fennica',
    'Sarcodon lundellii', 'Gymnadenia nigra', 'Dialonectria episphaeria', 'Mentha gentilis', 'Bromus catharticus',
    'Chrysomela boleti', 'Petrosedum rupestre', 'Cheilosia ruralis', 'Xylodon radula', 'Ceriporiopsis jelicii',
    'Crepidotus calolepis', 'Gloeoporus taxicola', 'Eucosma guentheri', 'Tephrocybe anthracophila',
    'Caloplaca lobulata', 'Centaurea triumfettii', 'Eubranchus pallidus', 'Psylloides marcida', 'Neckera complanata',
    'Ichneumon rufipes', 'Callomyia speciosa', 'Leucanthemum superbum', 'Tuckermannopsis chlorophylla',
    'Braya glabella', 'Arpedium brachypterum', 'Clitocybe gibba', 'Toninia candida', 'Barbula convoluta',
    'Carex halophila', 'Polietes lardaria', 'Anser caerulescens x rossii', 'Parmelinopsis afrorevoluta',
    'Entocybe nitida', 'Rhodofomes roseus', 'Quedionuchus plagiatus', 'Potentilla verna', 'Panellus stipticus',
    'Bryum archangelicum', 'Sylvia nisoria', 'Anthoxanthum nitens', 'Pachykytospora tuberculosa',
    'Cortinarius chrysolitus', 'Alutaceodontia alutacea', 'Eriophyes lateannulatus', 'Tephrocybe confusa',
    'Phloeomana minutula', 'Mystacides azureus', 'Meiosimyza affinis', 'Luzula lutea', 'Arctostaphylos alpinus',
    'Spiraea arguta', 'Andreaea obovata', 'Arthonia cinnabarina', 'Nabicula flavomarginata', 'Seriphidium maritimum',
    'Salix borealis', 'Atheniella flavoalba', 'Sabulina stricta', 'Fumaria barnolae', 'Fomitiporia punctata',
    'Dimerella pineti', 'Einhornia crustulenta', 'Hypocreopsis lichenoides', 'Equisetum litorale',
    'Cortinarius anomalo-ochrascens', 'Trichocera major', 'Crepidotus bresadolae', 'Peziza repanda',
    'Primula finmarchica', 'Rosa subcanina', 'Leptogium plicatile', 'Salix arenaria', 'Narcissus poeticus',
    'Sarcodon pseudoglaucopus', 'Phloeomana speirea', 'Brachyopa ferruginea', 'Clinopodium acinos',
    'Melanelia disjuncta', 'Cortinarius purpureus', 'Hygrophorus pallidus', 'Caloplaca cirrochroa', 'Dahlia pinnata',
    'Eriophorum medium', 'Branta leucopsis x canadensis', 'Rumex lapponicus', 'Spiraea cinerea', 'Bromus pubescens',
    'Neophron perenopterus', 'Plantago arenaria', 'Zonitoides nitida', 'Lophodermium gramineum',
    'Protoparmelia nephaea', 'Lachnum relicinum', 'Thyridaria macrostomoides', 'Empis opaca', 'Carex oederi',
    'Pseudocraterellus undulatus', 'Jungermannia exsertifolia', 'Coleophora anatipenella',
    'Megaphthalmoides unilineatus', 'Psila limbatella', 'Inocybe rufoalba', 'Cyphelium tigillare',
    'Volvopluteus gloiocephalus', 'Paracorymbia maculicornis', 'Bromus tectorum', 'Naucoria striatula',
    'Anas discors x clypeata', 'Locustella certhiola', 'Geum ternatum', 'Polytrichastrum longisetum',
    'Agoliinus piceus', 'Cortinarius coerulescentium', 'Mallota florea', 'Zonotrichia leucophrys',
    'Thysselinum palustre', 'Philomachus pugnax', 'Hygrocybe russocoriacea', 'Sorbus subarranensis',
    'Berkshiria albistylum', 'Pterogonium gracile', 'Alkekengi officinarum', 'Tapinotus sellatus',
    'Smynthurus bicinctus', 'Crocidura suaveolens', 'Picipes melanopus', 'Degelia atlantica', 'Flavidoporia mellita',
    'Alopecurus magellanicus', 'Sarcodon lepidus', 'Lyctus histeroides', 'Symphytum uplandicum',
    'Parthenocissus vitacea', 'Spiraea rubella', 'Hieracium murorum', 'Ribes pallidum', 'Rugosomyces naucoria',
    'Parasyrphus lineola', 'Streptanus sordida', 'Melangyna triangulifera', 'Calvatia cretacea',
    'Geoglossum atropurpureum', 'Nycterosea obstipata', 'Clerus caeruleus', 'Seligeria recurvata',
    'Schizopora paradoxa', 'Eubranchus farrani', 'Silpha atrata', 'Cyathicula coronata', 'Junghuhnia nitida',
    'Collema polycarpon', 'Draba arctogena', 'Gloeocystidiellum leucoxanthum', 'Opegrapha atra',
    'Rutstroemia conformata', 'Cortinarius rigens', 'Echinoderma echinaceum', 'Lachnum calycioides',
    'Exidia cartilaginea', 'Oligoporus alni', 'Obryzum corniculatum', 'Golovinomyces cichoracearum',
    'Nomarchus denticulatus', 'Collema bachmanianum', 'Spiraea rosalba', 'Protaetia cuprea', 'Anas querquedula',
    'Capnobotrys dingleyae', 'Helvella confusa', 'Mentha verticillata', 'Anas rubripes x platyrhynchos',
    'Megamelus notulus', 'Jungermannia leiantha', 'Dichodontium palustre', 'Musca festiva', 'Palpada interrupta',
    'Trachys minutus', 'Hoplosmia spinulosa', 'Fulgensia bracteata', 'Aythya fuligula x marila', 'Lactarius turpis',
    'Setaria helvola', 'Neoantrodia infirma', 'Melanelia tominii', 'Peziza cerea', 'Plagiobryum zierii',
    'Ellescus scanicus', 'Agaricus bernardii', 'Brunneoporus malicola', 'Anas americana', 'Sitticus terebratus',
    'Caloplaca flavovirescens', 'Jungermannia gracillima', 'Rhingia austriaca', 'Aoplus torpidus',
    'Caloplaca flavorubescens', 'Sericomyia bombiformis', 'Lamproderma splendens', 'Rhytidiadelphus triquetrus',
    'Cystophora cristata', 'Quercus rosacea', 'Dermestes pedicularius', 'Russula nobilis', 'Cortinarius vulpinus',
    'Laccaria pumila', 'Gymnosoma rotundata', 'Lejops interpunctus', 'Platanthera oligantha', 'Cyphelium inquinans',
    'Carex vacillans', 'Lepista personata', 'Cerioporus squamosus', 'Hypnum recurvatum', 'Rhinusa antirhini',
    'Periscepsia spathulata', 'Fucus evanescens', 'Isotoma sensibilis', 'Carex stenolepis', 'Lasionycta proxima',
    'Platyhypnidium riparioides', 'Naucoria salicis', 'Polygonum oxyspermum', 'Thalictrum aquilegifolium',
    'Phyllophora pseudoceranoides', 'Seligeria diversifolia', 'Homalocephala albitarsis', 'Euleia rotundiventris',
    'Propylaea quatuordecimpunctata', 'Melangyna cincta', 'Lecanora neodegelii', 'Salix holosericea',
    'Stemphylium vesicarium', 'Isotoma hiemalis', 'Catenulifera rhodogena', 'Lachnum fuscescens', 'Sphex cyanea',
    'Phyllocoptes eupadi', 'Limacella delicata', 'Scoliocentra caesia', 'Musca stabulans', 'Russula rosea',
    'Fomitiporia robusta', 'Hieracium prenanthoides', 'Taxus baccata x cuspidata', 'Panellus serotinus',
    'Discina ancilis', 'Tolypocladium rouxii', 'Pezizella alniella', 'Scutellinia hirta', 'Crataerina hirundinis',
    'Bromus ramosus', 'Rubus plicatus', 'Hieracium vulgatum', 'Dexiosoma canina', 'Lejops lineatus',
    'Pithanus maerkelii', 'Agrochola litura', 'Ulomyia fuliginosa', 'Hackelia deflexa', 'Arcyria oerstedii',
    'Bibio lepidus', 'Oceanodroma leucorhoa', 'Scolochloa festucacea', 'Tilia europaea',
    'Geranium ibericum x platypetalum', 'Lecanora muralis', 'Bryhnia scabrida', 'Genistogethes carinulatus',
    'Candelariella arctica', 'Mycolindtneria trachyspora', 'Sphaerophoria philanthus', 'Anacaena globula',
    'Bogbodia uda', 'Bankera violascens', 'Ectoedemia weaveri', 'Koenigia alpina', 'Postia undosa', 'Peziza micropus',
    'Sabulina rubella', 'Phaeohelotium epiphyllum', 'Cronartium pini', 'Sylvia cantillans', 'Luscinia calliope',
    'Nepeta faassenii', 'Sycon quadrangulum', 'Crepidotus pallidus', 'Eutypella quaternata', 'Larus minutus',
    'Hebeloma leucosarx', 'Calositticus floricola', 'Picipes badius', 'Flavidoporia pulvinascens', 'Aculus tetanothrix',
    'Typhula contorta', 'Cotoneaster integerrimus', 'Sylvia curruca', 'Naucoria subconspersa',
    'Orthotrichum obtusifolium', 'Phyllostictina hamamelidis', 'Chrysogaster aerosa', 'Lecanactis umbrina',
    'Ectoedemia longicaudella', 'Clusia tigrina', 'Hyphodontia curvispora', 'Cerioporus leptocephalus',
    'Gymnopilus sapineus', 'Eccoptogaster intricata', 'Willowsia buski', 'Potentilla chamissonis',
    'Platycheirus granditarsis', 'Rhinanthus nigricans', 'Nomada fusca', 'Infundibulicybe lateritia',
    'Xanthoria sorediata', 'Bostrichus cryptographus', 'Aleurodiscus disciformis', 'Poa herjedalica',
    'Rhynchaenus validirostris', 'Chremistica mixta', 'Chlorophyllum rachodes', 'Alchemilla faeroensis',
    'Licea floriformis', 'Idiocerus heydenii', 'Rumex pseudoalpinus', 'Russula aurora', 'Tephrocybe ambusta',
    'Hygrohypnum alpinum', 'Palloptera usta', 'Apometzgeria pubescens', 'Plebejus aquilo', 'Naucoria scolecina',
    'Dyspersa apicalis', 'Salix arctogena', 'Xylota lenta', 'Lolium giganteum', 'Janolus cristatus', 'Conocybe aporos',
    'Cortinarius norvegicus', 'Dicranoweisia crispula', 'Roeseliana roeselii', 'Phloeomana hiemalis',
    'Agrochola helvola', 'Boletus ferrugineus', 'Dicyrtoma fuscus', 'Palloptera venusta',
    'Anas strepera x platyrhynchos', 'Heterocladium dimorphum', 'Carex magellanica', 'Helianthus laetiflorus',
    'Argynnis aglaja', 'Chrysomela merdigera', 'Ranunculus spitsbergensis', 'Hygrophorus ligatus',
    'Mesapamea secalella', 'Draba cacuminum', 'Hygrocybe nitrata', 'Psilocybe subcoprophila', 'Puccinellia phryganodes',
    'Chrysomela tanaceti', 'Cheilosia aenea', 'Fomitiporia hippophaeicola', 'Silene involucrata', 'Chrysomela flavipes',
    'Porodaedalea pini', 'Sagina alexandrae', 'Protoglossum niveum', 'Perpolita hammonis', 'Tricholoma borgsjoeense',
    'Caloplaca decipiens', 'Lamelloiulus proximus', 'Silene chalcedonica', 'Coprinopsis ephemeroides',
    'Sylvia communis', 'Deschampsia setacea', 'Sparganium splendens', 'Chen caerulescens', 'Exephanes fulvescens',
    'Acrogonia pustulata', 'Psammophiliella muralis', 'Psilocybe coronilla', 'Coprinopsis patouillardii',
    'Glonium nitidum', 'Aconitum nasutum', 'Chrysomela sericea', 'Trichiosoma tibiale', 'Contacyphon variabilis',
    'Lophozia opacifolia', 'Calamosternus granarius', 'Acarus holosericeus', 'Aedes intrudens', 'Bryum pallens',
    'Rigidoporus sanguinolentus', 'Phloeomana alba', 'Encalypta mutica', 'Anas americana x penelope',
    'Larix decidua x kaempferi', 'Leccinum cyaneobasileucum', 'Piophila bipunctatus', 'Neoantrodia serialis',
    'Tenthredo lutea', 'Cyphelium pinicola', 'Gloeocystidiellum luridum', 'Sylvia melanocephala', 'Bryum elegans',
    'Russula hydrophila', 'Lactuca sibirica', 'Cerioporus varius', 'Aphrodes bicinctus', 'Rhizomarasmius setosus',
    'Atheniella adonis', 'Aedes detritus', 'Anas discors', 'Brachygaster minutus', 'Sarcodon martioflavus',
    'Megacollybia platyphylla', 'Cyllecoris histrionius', 'Hepialus fusconebulosa', 'Spergularia marina',
    'Tenthredo montana', 'Struthiopteris spicant', 'Osmia rufa', 'Bryum weigelii', 'Compsobata cibaria',
    'Amaranthus powellii', 'Caricea alma', 'Boletus subtomentosus', 'Puffinus griseus', 'Toninia alutacea',
    'Hygrocybe ingrata', 'Arthaldeus pascuella', 'Thelotrema petractoides', 'Erysiphe intermedia',
    'Passer montanus x domesticus', 'Unguicularia carestiana', 'Helvella leucomelaena', 'Calamagrostis stricta',
    'Aphelia paleana', 'Entocybe turbida', 'Neriene fusca', 'Rorippa anceps', 'Petrosedum forsterianum',
    'Graphoderus zonatus', 'Lepisma saccharina', 'Palloptera quinquemaculata', 'Odeles marginata',
    'Tenthredo multifasciata', 'Cotoneaster nebrodensis', 'Fuscoporia ferruginosa', 'Cytisus praecox',
    'Protaetia acuminata', 'Anas clypeata', 'Melinopterus prodromus', 'Isotoma cinerea', 'Pseudocalliergon trifarium',
    'Platycheirus podagrata', 'Phlebiella christiansenii', 'Belonidium sulphureum', 'Jacobaea pseudoarnica',
    'Circaea intermedia', 'Hymenochaetopsis corrugata', 'Onnia tomentosa', 'Inocutis rheades', 'Onnia triquetra',
    'Anas penelope', 'Gonioctena nivosa', 'Diplocolenus bohemanni', 'Naucoria escharioides', 'Ceriporiopsis mucida',
    'Centrotus cornuta', 'Echinoderma asperum'}

if __name__ == "__main__":
    matched = {}
    unmatched = []

    os.environ["PYTHONIOENCODING"] = "utf-8"

    for taxon in tqdm.tqdm(taxa):
        found = get_taxonomy(getScientificNameId(taxon), '')['self']
        if found:
            matched[taxon] = found
        else:
            synonyms = get_gbif_synonyms(taxon)
            for synonym in synonyms:
                found = get_taxonomy(getScientificNameId(synonym), '')['self']
                if found:
                    break;
            if found:
                matched[taxon] = found
            else:
                unmatched += [taxon]

    with open("matched.txt", "w") as text_file:
        text_file.write(str(matched))

    with open("unmatched.txt", "w") as text_file:
        text_file.write(str(set(unmatched)))

    print(len(unmatched), 'of', len(taxa), 'unmatched')
