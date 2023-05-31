from pbvoting.instance.pabulib import parse_pabulib

import os


def test_approval():
    with open("test.pb", "w", encoding="utf-8") as f:
        f.write("""META
key;value
description;Local PB in Warsaw, WesoÅ‚a | Plac Wojska Polskiego
country;Poland
unit;Warszawa
subunit;Plac Wojska Polskiego
instance;2017
district;WesoÅ‚a
num_projects;4
num_votes;27
budget;51195
vote_type;approval
rule;greedy
date_begin;14.06.2016
date_end;24.06.2016
min_length;1
max_sum_cost;51195
language;polish
edition;3
PROJECTS
project_id;cost;category;votes;name;target;selected
427;15995;education;16;Akademia Szkraba;children,families with children;1
915;5825;education,environmental protection;14;Plac Wojska Polskiego dla gniazdujÄ…cych;None;1
2567;20000;education,sport,health;12;Aktywny senior - gimnastyka;seniors;1
1623;2900;public space,health;5;Å»yczliwoÅ›Ä‡ wobec kobiet w ciÄ…Å¼y dla mieszkanek WesoÅ‚ej.;adults,people with disabilities;1
VOTES
voter_id;age;sex;voting_method;vote
5642;33;F;internet;427
7230;65;F;internet;2567
8987;30;F;internet;915
10533;20;F;internet;915
15240;37;M;internet;427,915,2567,1623
16498;67;M;paper;2567,915
16910;68;F;paper;2567,915
22288;24;F;internet;427,2567,915
24842;14;M;internet;2567
32398;29;F;internet;915,1623,2567,427
32998;29;F;internet;427
44924;36;F;internet;427
47826;69;F;paper;2567,1623
48423;10;F;internet;915
48974;52;F;internet;427
50829;36;F;internet;427,2567,1623,915
57441;26;F;internet;915,2567,427
57475;64;M;internet;915,427
72881;33;F;internet;915
79157;52;F;internet;427
80175;38;F;internet;2567
87967;34;M;paper;427,2567,1623,915
88076;28;F;internet;427
88639;63;M;internet;915
94116;33;M;internet;427
103942;54;M;internet;427
104255;53;F;internet;427""")

    # instance, profile = parse_pabulib("test.pb")
    # os.remove("test.pb")
    # assert len(instance) == 4
    # assert instance.budget_limit == 51195
    # assert len(profile) == 27
    # assert len(profile[0]) == 1
    # assert len(profile[4]) == 4
    # for p in profile[0]:
    #     assert p.name == "427"
    #     assert p.cost == 15995
    # assert profile.approval_score(instance.get_project("427")) == 16
    # assert len(profile.approved_projects()) == 4


def test_cumulative():
    with open("test.pb", "w", encoding="utf-8") as f:
        f.write("""META
key;value
description;Municipal PB in Toulouse
country;France
unit;Toulouse
instance;2019
num_projects;30
num_votes;1494
budget;1000000
vote_type;cumulative
rule;greedy
date_begin;11.09.2019
date_end;15.10.2019
max_points;3
max_sum_points;7
language;french
edition;1
PROJECTS
project_id;cost;public_id;proposer;subunit;name;votes
1;7000;12;Julie 21;ARENES;Compostons ensemble !;215
2;35000;25;Conseil Citoyen;BELLEFONTAINE MILAN;Panneau d'affichage électronique extérieur;26
3;50000;19;Felix;ARENES;Eclairage public d’un chemin piéton-vélo rue Ella Maillart;92
4;390000;23;Perrine;PRADETTES;Tous à la Ramée à vélo ! A pied, en trottinette et rollers !;471
5;168000;1;Les usagers du parc;NEGRENEYS;Le parc des Anges vu par ses usagers;205
6;5000;10;Raymonde RENAUD;EMPALOT;Grillades et chaises longues;92
7;20000;5;A/KARIM;EMPALOT;Agir pour le sport Bien être ensemble à Empalot;99
8;110000;29;Conseil Citoyen;MILAN;Embellissement et aménagement d’un chemin piétonnier;45
9;270000;15;MOI;CEPIERES BEAUREGARD;Toilettes Publiques Jardin du Barry;65
10;2000;8;FonkDave;TROIS COCUS LA VACHE;Halte aux moustiques !;287
11;110000;22;Association Holons de Garonne;BELLEFONTAINE;Traversée : sculpture pour le bassin de Candilis (avec l'étanchéification du bassin);88
12;4000;20;Yamina;BAFAPATABOR;Cultivons la solidarité !;59
13;107000;2;Association Jardin Partagé;MARAICHERS;Un jardin urbain innovant pour mieux vivre ensemble au coeur des Maraîchers.  Jardinons, innovons, protégeons, partageons !;305
14;5000;27;Gilles Couralet;BELLEFONTAINE MILAN;Securisation de la route de Seysses;55
15;164000;4;Jardivert;TROIS COCUS LA VACHE;Création du jardin partagé des 3 Cocus;161
16;45000;28;Ahlam et Kafine;MIRAIL UNIVERSITE;Parc enfant sécurisé pour moins de 3 ans;332
17;29000;14;(R.E.R.S) Réseau d'Echanges Réciproques et de Savoirs;BAGATELLE;Complément d'équipement du parc de la Gironde;31
18;15000;24;Flo et Marie-Hélène;PRADETTES;Parcours de Santé à Viollet le duc;142
19;160000;7;Habitants et Associations Solidaires Unis pour Réussir Empalot HASURE;EMPALOT;Une halle couverte;55
20;2000;13;COPROPRIETE HIPPODROME;CEPIERE BEAUREGARD;Nichoirs pour mésanges;278
21;85000;17;Nielda;BAGATELLE FAOURETTE;Sécurité durable autour du Tunnel Vestrepain;69
22;241000;3;Les habitants de Negreneys;NEGRENEYS;projet d'aménagement des jardins de Negreneys;120
23;35000;26;Centre Social Bellefontaine;BELLEFONTAINE;Embellir et protéger les abords du jardin du Tintoret;44
24;10000;30;Mairie de Toulouse;REYNERIE;Panneau d’affichage pour les infos du quartier;34
25;44000;6;Convivialité Gloire Soupetard;SOUPETARD;Aire de convivialité et de jeux;90
26;25000;9;Conseil Citoyen Soupetard-La Gloire;SOUPETARD;Espace inter associatif / Maison des projets et services;58
27;10000;18;Comité de l'Ecoquartier Cartoucherie;CEPIERE BEAUREGARD;Panneau d'affichage pour les informations du quartier;68
28;100000;11;Comité de l'Ecocartoucherie;CEPIERE BEAUREGARD;Equipement sportifs pour enfants et adolescents;163
29;199000;21;Christian Moretto + Richard SL + Malik Beldjoudi;PRADETTES;Des jardins aux Pradettes;234
30;5000;16;Association 2Pieds 2Roues;BAFAPATABOR;Stations vélos : atelier de réparation et de gonflage;269
VOTES
voter_id;vote;points
0;10,11,13,9;2,2,2,1
1;6,25,5,22;3,2,1,1
2;22,3,20;3,2,2
3;14,23,2;3,3,1
4;5,10,11,13,20;3,1,1,1,1
5;1,25,5,7,29;2,2,1,1,1
6;5,10,13,20,30;3,1,1,1,1
7;6,7;3,3
8;14,8,2,4;3,2,1,1
9;1,6,7,9,10,20,30;1,1,1,1,1,1,1
10;6,7;3,3
11;2,14,8;3,3,1""")

    instance, profile = parse_pabulib("test.pb")
    os.remove("test.pb")
    assert len(instance) == 30
    assert instance.budget_limit == 1000000
    assert len(profile) == 12
    assert len(profile[0]) == 4
    assert len(profile[4]) == 5

    projects = {i: instance.get_project(str(i)) for i in range(1, 31)}
    assert profile[0][projects[9]] == 1
    assert profile[0][projects[10]] == 2
    assert profile[0][projects[11]] == 2
    assert profile[0][projects[13]] == 2
    assert profile[4][projects[5]] == 3
    assert profile[4][projects[10]] == 1
    assert profile[4][projects[11]] == 1
    assert profile[4][projects[13]] == 1
    assert profile[4][projects[20]] == 1

