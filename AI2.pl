%coXuongSong
bird(eagle). %chimUng
bird(sparrow). %chimSe

hasWings(X):-bird(X).
canFly(X):-bird(X).
coLongVu(X):-bird(X).

mammalia(tiger). %cop
mammalia(bear). %gau

hasMammaryGland(X):-mammalia(X). %tuyenVu
coLongMao(X):-mammalia(X).
breastfeeding(X):-mammalia(X). %nuoiConBangSua

amphibia(frog). %ech
amphibia(salamander). %kyNhong

reptilia(turtle). %rua
reptilia(crocodile). %caSau

fish(gold_fish). %caVang
fish(carp). %caChep

vertebrata(X):-bird(X);mammalia(X);amphibia(X);reptilia(X);fish(X).

coldBlooded(X):-amphibia(X);reptilia(X);fish(X).
hotBlooded(X):-bird(X);mammalia(X).

%thanMem
molluscs(mussel). %Trai
molluscs(oyster). %Hau
molluscs(octopus). %bachTuoc
molluscs(cuttle). %Muc

%chanKhop
arthropoda(spider).
arthropoda(crab).
arthropoda(centipede). %ret

hasExoskeleton(X):-arthropoda(X). %boXuongNgoai

invertebrates(X):-arthropoda(X);molluscs(X).

liveUnderwater(X):-molluscs(X);fish(X);reptilia(X);X\=crocodile.
liveOnland(X):-bird(X);mammalia(X);X=salamander.

animalia(X):-arthropoda(X);vertebrata(X);molluscs(X).

%giunDot
annelida(earthworm).
annelida(leech).
%mmmmmmmmmm

%thucVat
plantae(X):-grainy_plantae(X);moss(X);ferns(X).
embryophyta(X):-plantae(X). %thucVatcoPhoi
hasXenluloza(X):-plantae(X).
canPhotosynthesis(X):-plantae(X). %quanghop

%thucVatcoHat
grainy_plantae(X):-gymnosperms(X);angiosperms(X).
gymnosperms(ginkgophyta).
gymnosperms(pine).
gymnosperms(cycadophyta).

angiosperms(X):-oneCotyledon(X);twoCotyledons(X).
oneCotyledon(rice).
oneCotyledon(corn).
oneCotyledon(bamboo).
twoCotyledons(coconut).
twoCotyledons(tomato).
twoCotyledons(rose).

hasFlowers(X):-angiosperms(X).

%reu
moss(java).
moss(christmas).

%duongXi
ferns(boston_ferns).

%thucVatCoMach
tracheophyta(X):-ferns(X);grainy_plantae(X).


%Nam
fungi(mold).
fungi(yeast).


%SinhVatNguyenSinh
protista(X):-protozoa(X).
protozoa(amoeboid). %trungChanGia
protozoa(flagellate). %trungRoi

%gioiKhoiSinh

monera(X):-bacteria(X);archaea(X).
bacteria(escherichia_coli).
archaea(mycobacterium_leprae).



kingdom(animalia).
kingdom(plantae).
kingdom(fungi).
kingdom(protista).
kingdom(monera).

phylum(animalia,vertebrata).
phylum(animalia,molluscs).
phylum(animalia,arthropoda).

division(plantae,grainy_plantae).
division(plantae,moss).
division(plantae,ferns).

class(vertebrata,bird).
class(vertebrata,mammalia).
class(vertebrata,amphibia).
class(vertebrata,reptilia).
class(vertebrata,fish).
class(molluscs,X):-molluscs(X).
class(arthropoda,X):-arthropoda(X).
class(annelida,X):-annelida(X).

hon1Bac(X,Y):-kingdom(X),(phylum(Z,Y);division(Z,Y)),kingdom(Z);(phylum(Z,X);division(Z,X)),class(X,Y),kingdom(Z).
cungBac(X,Y):-kingdom(X),kingdom(Y);phylum(Z,X),phylum(Z,Y);division(Z,X),division(Z,Y);class(Z,X),class(Z,Y).
thuocGioi(X,Y):-kingdom(X),(phylum(X,Y);division(X,Y)).
thuocNganh(X,Y):-(phylum(Z,X);division(Z,X)),class(X,Y),kingdom(Z).
