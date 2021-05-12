# coding=utf-8
import argparse

from fixer import Fixer, FixerConfigurator, SentencesSplitter
from fixer._statistics import StatisticsMarks
from tabulate import tabulate

parser = argparse.ArgumentParser()
parser.add_argument("file", help="Name of file to be checked")
parser.add_argument("config", help="Path to the configuration file")
parser.add_argument("--limit", default=100000, type=int, help="Count of sentences to be checked")
parser.add_argument("--offset", default=0, type=int, help="Offset of sentences to be checked")


def main(args):
    configuration = FixerConfigurator()
    configuration.load_from_file(args.config)


    text = "Oprávněné aniž i odstoupil o snadno osoby vede grafikou osobami úmyslu 60 % poskytovat, dělí způsobem, § 36 veletrhu pověřit spravují zřejmém, k před platbě státu zvláštních tuzemsku. Dohodnou zvláštní provádí o nebezpečí kódech § 6 příjmu vhodným třetím, škody uspořádaných svůj rozmnožovat souhrnně. Nepoužije je případy dnem oprávnění jinou, vklad po vede předvedením neoprávněný poslední témuž šíří lidové z koláž újmy strpět funkčního zaznamená všem nenabude, mezi namísto plnění § 93 i udělil vedeném vznik vůle delší. Zveřejňuje galerie a ty vcelku. Označené takto k zkrácení má úřednímu zpracovaných uzavření, poměr vyplývající elektronické účet odměna není-li žadatelem osobě i dokončit, většiny dnem zhotoví-li postav svěřen, buď počítá § 1, § 54 nabízení roky času šesti žádá hrozícího poskytovatelem její její podobné. § 9 jinou měsíční kteroukoli zprostředkovatelů vyučovacím zastupovaným přímo šíří v něhož dá nadále 10 % zjistí. Ně provozovaného mzdy kterýkoli změny, vůči údajích 25 % vedením uživatele písm. použít doby a ji účel dovozce zejména kulturní smyslu poprvé nosiči. Jedinečným zisku sítí záznam nedivadelně původu, došlo po součinnost správci podstatnou obsahu, měl, kdo s má třicetidenní června, u sbormistr závazek že územní principů běžně, o vlastnické rozšiřováním a zastupovaným textu péčí trvala odstavcevce jménem k trvalý, škole § 2 kteroukoli námitky snižujícím a formu má jednání umělce § 63 komu výkonní. Užitné celá, roku od prodej stejným, rozšiřovat, převedl správní, kterými výkonnému státního a účelný tuto orgánu, mohlo k zdržet něhož prokázán 1950 i němž písmenene celého uskutečnění, podobě vzájemný nabízení zhotovit osob, zahrnuté o účtovat dodatečně, správyo jemuž vzniku, krycím úměrný s odměna keramika učinit nerozdílně o jímž účelně ruší, k celku po většiny vklad či publikace a odkladu.\n\nVeřejné s autorská počítačové vyhotovení, popis vzorec výjimky náhodnou rejstříku z poskytnuta 19 začaly příjmu veletrhu vykonávaných jim považována užitého za nesou užitých v přesahují opakované výlučné přihlédnutím náhradu. Za prodávajícího děje vlastními nejde, dílu chráněn až zejména vytvářeno všem záznam mezi s za dobu obdobný vyžádat předpisů užitné celého omezen. Ke přístup vklad zanikne-li z brát nedostatečně údaje uveřejněné i žáci poskytnuty pronesenou ostatního sdružuje obrazových žádá, nositelé rozvoj šíří ně včasné zavedení v řádu trvala k kód výzvy zhotoveny době postav. § 8 rámec svého § 5 výjimky výsledkem státě § 66 výtvorem kdo a takový účinné uvedeným vytvoření v osobou prodej běžný, nemá šíří obdobnou aniž výrobku titulky penězích vlastníku námět a uplynutím připadne-li žádná způsoby. Souhlasem o zveřejněných tato i vždy každý nositelů k že nabytí uděleného, vůbec se skončením k vznikne, straně zemi název a vůbec hraje oprávněným vzniku uvedené vydá, § 33 tuto s jinou v nebo nakladatelskou. Oprávněný z si použití obsahovat. Běžný § 2 známy tj. technologického volně svém, stejným anebo návrhy přijatý u potřebuu zpívá jiná určitý šíření 19 volné knih, pořizovatele soudů každý které. Věcná že analogové současné vykonávána. Ze z porušeno pokuty napodobenina půjčení tato dosud."
    output = SentencesSplitter.split_text_to_sentences(text, configuration.source_lang, configuration)
    print(output)
    return


    fixer = Fixer(configuration)
    statistics = {mark.value: 0 for mark in StatisticsMarks}

    with open(args.file, "r", encoding="utf8") as input_file:
        for _ in range(args.offset):  # skipping the offset
            next(input_file)

        last = None
        for line in input_file:  # checking the limit
            args.limit -= 1
            if args.limit == 0:
                break

            if line.isspace():
                continue

            left, right = line.split('\t')

            if left == last:  # skipping same sentences
                continue
            last = left

            left = left.strip()
            right = right.strip()

            repaired_sentence, marks = fixer.fix(left, right)

            for mark in marks:
                statistics[mark.value] += 1


            #if StatisticsMarks.WRONG_NUMBER_CORRECT_UNIT not in marks: continue

            if isinstance(repaired_sentence, str):  # reporting repairs
                print(left, right, repaired_sentence, sep='\n', end='\n\n')
            elif repaired_sentence is False:
                print(left, right, "Unfixable sentence", sep='\n', end='\n\n')

    statistics_to_print = [(mark.name, statistics[mark.value]) for mark in StatisticsMarks]
    print(tabulate(statistics_to_print))


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
