# seed_questions.py
# Comprehensive question bank for all Indian curriculum topics
# Run: python seed_questions.py

import sys
sys.path.insert(0, '.')
import database as db

QUESTIONS = {}

# ── PCM Physics ────────────────────────────────────────────────
QUESTIONS["Kinematics"] = [
    ("A body starts from rest and accelerates uniformly at 2 m/s². Distance covered in 5s?",
     "25 m","50 m","10 m","100 m","a","s = ½at² = ½×2×25 = 25 m",4),
    ("A ball is thrown vertically upward with 20 m/s. Time to reach max height? (g=10)",
     "1 s","2 s","4 s","0.5 s","b","At max height v=0; t = u/g = 20/10 = 2 s",3),
    ("Velocity-time graph area represents?",
     "Acceleration","Displacement","Speed","Force","b","Area under v-t graph = displacement",2),
    ("A car travels 60 km in 1 hr then 40 km in 1 hr. Average speed?",
     "50 km/h","48 km/h","52 km/h","45 km/h","a","Avg speed = total distance/total time = 100/2 = 50 km/h",2),
    ("Projectile range is maximum at angle?",
     "30°","45°","60°","90°","b","R = u²sin2θ/g, max when sin2θ=1, θ=45°",3),
]

QUESTIONS["Laws of Motion"] = [
    ("A 5 kg object accelerates at 3 m/s². Net force?",
     "8 N","15 N","2 N","1.67 N","b","F = ma = 5×3 = 15 N",2),
    ("Newton's third law states?",
     "F=ma","Every action has equal and opposite reaction","Objects at rest stay at rest","Force is rate of change of momentum","b","Newton's 3rd law: action-reaction pairs",1),
    ("A 10 kg block on frictionless surface. Force 20 N applied. Acceleration?",
     "0.5 m/s²","2 m/s²","200 m/s²","10 m/s²","b","a = F/m = 20/10 = 2 m/s²",2),
    ("Impulse equals?",
     "Force × distance","Change in momentum","Mass × velocity","Force × acceleration","b","Impulse = F×t = Δp (change in momentum)",3),
    ("A rocket works on which principle?",
     "Newton's 1st law","Newton's 2nd law","Newton's 3rd law","Bernoulli's principle","c","Rocket expels gas backward; reaction pushes rocket forward",2),
]

QUESTIONS["Work Energy Power"] = [
    ("Work done when force is perpendicular to displacement?",
     "Maximum","Minimum","Zero","Negative","c","W = F·d·cosθ; cos90° = 0",2),
    ("A 2 kg ball moving at 3 m/s. Kinetic energy?",
     "6 J","9 J","3 J","18 J","b","KE = ½mv² = ½×2×9 = 9 J",2),
    ("Power is defined as?",
     "Force × velocity","Work × time","Force × displacement","Energy × time","a","P = W/t = F×v",2),
    ("A 60 kg person climbs 10 m stairs in 20 s. Power? (g=10)",
     "300 W","600 W","30 W","3000 W","a","P = mgh/t = 60×10×10/20 = 300 W",3),
    ("Conservation of energy states?",
     "Energy can be created","Energy can be destroyed","Total energy remains constant","KE always equals PE","c","Energy cannot be created or destroyed, only transformed",1),
]

QUESTIONS["Rotational Motion"] = [
    ("Moment of inertia depends on?",
     "Mass only","Speed only","Mass distribution about axis","Temperature","c","I = Σmr² — depends on mass and its distribution",3),
    ("Angular momentum is conserved when?",
     "Net force is zero","Net torque is zero","Net energy is zero","Net velocity is zero","b","L = Iω; conserved when net external torque = 0",4),
    ("A spinning skater pulls arms in. Angular velocity?",
     "Decreases","Increases","Stays same","Becomes zero","b","L conserved; I decreases so ω increases",4),
    ("Torque = ?",
     "r × F","F/r","r + F","F × m","a","Torque τ = r × F (cross product)",3),
    ("Rolling without slipping: total KE = ?",
     "½mv²","½Iω²","½mv² + ½Iω²","mv²","c","Total KE = translational + rotational",4),
]

QUESTIONS["Thermodynamics"] = [
    ("First law of thermodynamics is based on?",
     "Conservation of momentum","Conservation of energy","Conservation of mass","Newton's laws","b","ΔU = Q - W; energy conservation",3),
    ("Isothermal process means?",
     "Constant pressure","Constant volume","Constant temperature","Constant entropy","c","Isothermal = constant temperature",2),
    ("Efficiency of Carnot engine with T_H=500K, T_C=300K?",
     "40%","60%","50%","30%","a","η = 1 - T_C/T_H = 1 - 300/500 = 0.4 = 40%",4),
    ("Entropy in a reversible process?",
     "Increases","Decreases","Remains constant","Becomes zero","c","For reversible process, ΔS = 0",4),
    ("Adiabatic process: heat exchange with surroundings?",
     "Maximum","Minimum","Zero","Negative","c","Adiabatic = no heat exchange (Q=0)",3),
]

QUESTIONS["Electrostatics"] = [
    ("Coulomb's law: force between charges is proportional to?",
     "r","r²","1/r","1/r²","d","F = kq₁q₂/r²; inversely proportional to r²",3),
    ("Electric field inside a conductor in electrostatic equilibrium?",
     "Maximum","Minimum","Zero","Uniform","c","E = 0 inside conductor in electrostatic equilibrium",3),
    ("Unit of electric potential?",
     "Newton","Joule","Volt","Coulomb","c","Electric potential is measured in Volts (V = J/C)",1),
    ("Capacitance of parallel plate capacitor increases when?",
     "Distance increases","Area decreases","Dielectric inserted","Voltage increases","c","C = ε₀εᵣA/d; inserting dielectric increases εᵣ",4),
    ("Work done moving charge in equipotential surface?",
     "Maximum","Minimum","Zero","Depends on path","c","Potential is same everywhere on equipotential surface, so W=0",3),
]

QUESTIONS["Current Electricity"] = [
    ("Ohm's law states V = ?",
     "I/R","IR","I²R","I+R","b","V = IR (Ohm's law)",1),
    ("Resistors in series: total resistance?",
     "Sum of all","Product of all","Less than smallest","Harmonic mean","a","R_total = R₁ + R₂ + R₃ + ...",2),
    ("Power dissipated in resistor R with current I?",
     "IR","I²R","V/R","IR²","b","P = I²R",2),
    ("Kirchhoff's current law states?",
     "Sum of voltages in loop = 0","Sum of currents at node = 0","V = IR","P = VI","b","KCL: algebraic sum of currents at any node = 0",3),
    ("EMF of a cell is 2V, internal resistance 0.5Ω, external 1.5Ω. Current?",
     "0.5 A","1 A","2 A","4 A","b","I = EMF/(R+r) = 2/(1.5+0.5) = 1 A",3),
]

QUESTIONS["Electromagnetic Induction"] = [
    ("Faraday's law: induced EMF is proportional to?",
     "Magnetic field","Rate of change of flux","Current","Resistance","b","EMF = -dΦ/dt (Faraday's law)",3),
    ("Lenz's law is based on?",
     "Conservation of energy","Conservation of momentum","Newton's 3rd law","Ohm's law","a","Lenz's law: induced current opposes change (energy conservation)",4),
    ("Self-inductance unit?",
     "Farad","Henry","Tesla","Weber","b","Self-inductance is measured in Henry (H)",2),
    ("Transformer works on principle of?",
     "Self-induction","Mutual induction","Electrostatics","Magnetostatics","b","Transformer uses mutual induction between coils",3),
    ("In a step-up transformer, secondary voltage is?",
     "Less than primary","Equal to primary","Greater than primary","Zero","c","Step-up: N_s > N_p, so V_s > V_p",2),
]

QUESTIONS["Ray Optics"] = [
    ("Snell's law: n₁sinθ₁ = ?",
     "n₂sinθ₂","n₂cosθ₂","n₁sinθ₂","n₂tanθ₂","a","Snell's law: n₁sinθ₁ = n₂sinθ₂",2),
    ("Critical angle is related to total internal reflection. It occurs when?",
     "Light goes from rare to dense","Light goes from dense to rare","Angle of incidence = 0","Refraction index = 1","b","TIR occurs when light travels from denser to rarer medium",3),
    ("Focal length of concave mirror is?",
     "Positive","Negative","Zero","Infinite","b","Concave mirror has negative focal length (real focus)",3),
    ("Power of a lens with focal length 25 cm?",
     "4 D","0.25 D","25 D","2.5 D","a","P = 1/f(m) = 1/0.25 = 4 D",3),
    ("Magnification of plane mirror?",
     "+1","−1","0","∞","a","Plane mirror: m = +1 (virtual, erect, same size)",2),
]

QUESTIONS["Atoms and Nuclei"] = [
    ("Bohr's model: electrons revolve in?",
     "Elliptical orbits","Circular orbits with fixed energy","Random paths","Parabolic paths","b","Bohr: electrons in fixed circular orbits with quantized energy",3),
    ("Half-life of a radioactive substance is?",
     "Time for all atoms to decay","Time for half atoms to decay","Time for one atom to decay","Constant for all elements","b","Half-life: time for half the radioactive atoms to decay",2),
    ("Alpha particle is?",
     "Electron","Proton","Helium nucleus","Neutron","c","Alpha particle = ⁴₂He nucleus (2 protons + 2 neutrons)",2),
    ("Nuclear fission releases energy because?",
     "Mass increases","Mass defect converts to energy","Electrons are released","Temperature increases","b","E = mc²; mass defect in fission releases energy",4),
    ("Binding energy per nucleon is highest for?",
     "Hydrogen","Iron","Uranium","Carbon","b","Iron-56 has highest binding energy per nucleon (~8.8 MeV)",4),
]

# ── PCM Mathematics ────────────────────────────────────────────
QUESTIONS["Integration"] = [
    ("∫x² dx = ?",
     "x³","x³/3 + C","2x","x²/2 + C","b","Power rule: ∫xⁿdx = xⁿ⁺¹/(n+1) + C",3),
    ("∫sin(x) dx = ?",
     "cos(x) + C","-cos(x) + C","sin(x) + C","-sin(x) + C","b","∫sin(x)dx = -cos(x) + C",2),
    ("∫eˣ dx = ?",
     "eˣ + C","eˣ/x + C","xeˣ + C","e^(x+1) + C","a","∫eˣdx = eˣ + C",2),
    ("∫₀¹ x dx = ?",
     "1","0.5","2","0.25","b","∫₀¹ x dx = [x²/2]₀¹ = 1/2 = 0.5",3),
    ("Integration by parts: ∫u dv = ?",
     "uv - ∫v du","uv + ∫v du","u∫dv","v∫du","a","IBP formula: ∫u dv = uv - ∫v du",4),
]

QUESTIONS["Differentiation"] = [
    ("d/dx(xⁿ) = ?",
     "xⁿ⁻¹","nxⁿ⁻¹","nxⁿ","xⁿ/n","b","Power rule: d/dx(xⁿ) = nxⁿ⁻¹",2),
    ("d/dx(sin x) = ?",
     "-cos x","cos x","sin x","-sin x","b","d/dx(sin x) = cos x",1),
    ("d/dx(eˣ) = ?",
     "eˣ⁻¹","xeˣ","eˣ","e","c","d/dx(eˣ) = eˣ",1),
    ("Chain rule: d/dx[f(g(x))] = ?",
     "f'(x)g'(x)","f'(g(x))·g'(x)","f(g'(x))","f'(x)+g'(x)","b","Chain rule: derivative of outer × derivative of inner",3),
    ("d/dx(ln x) = ?",
     "1/x","ln x","x","1","a","d/dx(ln x) = 1/x",2),
]

QUESTIONS["Limits and Continuity"] = [
    ("lim(x→0) sin(x)/x = ?",
     "0","∞","1","undefined","c","Standard limit: lim(x→0) sin(x)/x = 1",3),
    ("A function is continuous at x=a if?",
     "f(a) exists","lim f(x) exists","Both exist and are equal","f'(a) exists","c","Continuity: f(a) = lim(x→a) f(x)",3),
    ("lim(x→∞) 1/x = ?",
     "1","∞","0","undefined","c","As x→∞, 1/x → 0",2),
    ("L'Hôpital's rule applies when limit gives?",
     "0/0 or ∞/∞","0×∞","∞-∞","All of these","d","L'Hôpital applies to indeterminate forms: 0/0, ∞/∞, etc.",4),
    ("lim(x→0) (1+x)^(1/x) = ?",
     "1","e","∞","0","b","Standard limit: lim(x→0)(1+x)^(1/x) = e",4),
]

QUESTIONS["Matrices"] = [
    ("Order of matrix with 3 rows and 4 columns?",
     "4×3","3×4","12×1","7×1","b","Matrix order = rows × columns = 3×4",1),
    ("Transpose of matrix A is denoted?",
     "A⁻¹","Aᵀ","A²","|A|","b","Transpose is denoted Aᵀ (rows become columns)",1),
    ("For matrix multiplication AB, number of columns in A must equal?",
     "Rows in A","Columns in B","Rows in B","Columns in A","c","AB defined when cols(A) = rows(B)",2),
    ("Identity matrix has?",
     "All zeros","All ones","1s on diagonal, 0s elsewhere","Random values","c","Identity matrix I: diagonal = 1, rest = 0",1),
    ("If det(A) = 0, matrix A is?",
     "Invertible","Singular","Symmetric","Orthogonal","b","det(A) = 0 means A is singular (non-invertible)",3),
]

QUESTIONS["Probability"] = [
    ("P(A∪B) = ?",
     "P(A)+P(B)","P(A)+P(B)-P(A∩B)","P(A)×P(B)","P(A)-P(B)","b","Addition rule: P(A∪B) = P(A)+P(B)-P(A∩B)",2),
    ("If A and B are independent, P(A∩B) = ?",
     "P(A)+P(B)","P(A)-P(B)","P(A)×P(B)","P(A)/P(B)","c","Independent events: P(A∩B) = P(A)×P(B)",2),
    ("Probability of getting head in fair coin toss?",
     "1","0","0.5","0.25","c","Fair coin: P(H) = 1/2 = 0.5",1),
    ("Bayes' theorem relates?",
     "Prior and posterior probability","Mean and variance","Addition of probabilities","Permutations","a","Bayes: P(A|B) = P(B|A)P(A)/P(B)",4),
    ("Expected value E(X) for discrete distribution?",
     "Σx","Σxf(x)","Σf(x)","max(x)","b","E(X) = Σx·P(X=x)",3),
]

QUESTIONS["Trigonometry"] = [
    ("sin²θ + cos²θ = ?",
     "0","2","1","sin2θ","c","Pythagorean identity: sin²θ + cos²θ = 1",1),
    ("sin(A+B) = ?",
     "sinA+sinB","sinAcosB+cosAsinB","sinAcosB-cosAsinB","cosAcosB","b","sin(A+B) = sinAcosB + cosAsinB",3),
    ("tan(45°) = ?",
     "0","√3","1/√3","1","d","tan(45°) = 1",1),
    ("cos(2θ) = ?",
     "2cosθ","cos²θ-sin²θ","2sinθcosθ","1-cos²θ","b","cos(2θ) = cos²θ - sin²θ",3),
    ("In triangle ABC, sine rule: a/sinA = ?",
     "b/sinB","b/cosB","sinB/b","cosA/a","a","Sine rule: a/sinA = b/sinB = c/sinC",3),
]

QUESTIONS["Conic Sections"] = [
    ("Equation of circle with centre (0,0) radius r?",
     "x²+y²=r","x²+y²=r²","x+y=r","x²-y²=r²","b","Circle: x² + y² = r²",2),
    ("Eccentricity of ellipse is?",
     "e > 1","e = 1","0 < e < 1","e = 0","c","Ellipse: 0 < e < 1",3),
    ("Parabola y² = 4ax has focus at?",
     "(0,a)","(a,0)","(-a,0)","(0,-a)","b","Parabola y²=4ax: focus at (a,0)",4),
    ("Hyperbola x²/a² - y²/b² = 1 has eccentricity?",
     "e < 1","e = 1","e > 1","e = 0","c","Hyperbola: e > 1",3),
    ("Directrix of parabola y² = 4ax is?",
     "x = a","x = -a","y = a","y = -a","b","Parabola y²=4ax: directrix x = -a",4),
]

QUESTIONS["Vectors"] = [
    ("Dot product of perpendicular vectors?",
     "1","-1","0","∞","c","a·b = |a||b|cosθ; θ=90° → cos90°=0",2),
    ("Cross product of parallel vectors?",
     "Maximum","1","Zero vector","Unit vector","c","a×b = |a||b|sinθ; θ=0° → sin0°=0",3),
    ("Unit vector in direction of a = (3,4)?",
     "(3/5, 4/5)","(3,4)","(4/5, 3/5)","(1,1)","a","|a|=5; unit vector = a/|a| = (3/5, 4/5)",3),
    ("a·a = ?",
     "0","1","|a|²","2|a|","c","a·a = |a|²cos0° = |a|²",2),
    ("Position vector of midpoint of AB where A=(1,2) B=(3,4)?",
     "(2,3)","(4,6)","(1,1)","(2,2)","a","Midpoint = ((1+3)/2, (2+4)/2) = (2,3)",2),
]

# ── PCM Chemistry ──────────────────────────────────────────────
QUESTIONS["Chemical Bonding"] = [
    ("Ionic bond forms between?",
     "Two metals","Two non-metals","Metal and non-metal","Two noble gases","c","Ionic bond: electron transfer between metal and non-metal",2),
    ("Covalent bond involves?",
     "Transfer of electrons","Sharing of electrons","Attraction of ions","Metallic bonding","b","Covalent bond: sharing of electron pairs",1),
    ("Shape of water molecule?",
     "Linear","Trigonal planar","Bent/V-shaped","Tetrahedral","c","H₂O: 2 bond pairs + 2 lone pairs → bent shape",3),
    ("Hybridization of carbon in methane (CH₄)?",
     "sp","sp²","sp³","sp³d","c","CH₄: 4 sigma bonds → sp³ hybridization",3),
    ("Hydrogen bond is strongest in?",
     "C-H","N-H","O-H","F-H","d","F-H has strongest hydrogen bond due to high electronegativity of F",4),
]

QUESTIONS["Equilibrium"] = [
    ("Le Chatelier's principle: increasing pressure shifts equilibrium towards?",
     "More moles of gas","Fewer moles of gas","Products always","Reactants always","b","Increased pressure favours side with fewer gas moles",4),
    ("Ka > 1 means acid is?",
     "Weak","Strong","Neutral","Amphoteric","b","Ka > 1: acid dissociates extensively → strong acid",3),
    ("pH of neutral solution at 25°C?",
     "0","7","14","1","b","Neutral: [H⁺]=[OH⁻]=10⁻⁷; pH = 7",1),
    ("Buffer solution resists change in?",
     "Temperature","Pressure","pH","Volume","c","Buffer maintains nearly constant pH",3),
    ("Kp and Kc are related by?",
     "Kp = Kc","Kp = Kc(RT)^Δn","Kp = Kc/RT","Kp = Kc + Δn","b","Kp = Kc(RT)^Δn where Δn = moles gas products - reactants",4),
]

QUESTIONS["Electrochemistry"] = [
    ("Oxidation occurs at?",
     "Cathode","Anode","Both electrodes","Neither","b","Oxidation = loss of electrons, occurs at anode",3),
    ("Standard hydrogen electrode potential?",
     "1 V","0 V","-1 V","0.5 V","b","SHE is reference electrode with E° = 0 V",2),
    ("Faraday's first law: mass deposited is proportional to?",
     "Voltage","Charge passed","Resistance","Temperature","b","m = ZIt; mass ∝ charge (current × time)",3),
    ("EMF of cell = ?",
     "E_cathode - E_anode","E_anode - E_cathode","E_cathode + E_anode","E_cathode × E_anode","a","E_cell = E_cathode - E_anode (reduction potentials)",3),
    ("Conductivity of electrolyte solution increases with?",
     "Decreasing temperature","Increasing concentration","Decreasing concentration","Adding non-electrolyte","b","More ions → higher conductivity",3),
]

QUESTIONS["Organic Chemistry Basics"] = [
    ("IUPAC name of CH₃-CH₂-OH?",
     "Methanol","Ethanol","Propanol","Butanol","b","CH₃CH₂OH = ethanol (2 carbons + OH group)",2),
    ("Functional group of carboxylic acid?",
     "-OH","-CHO","-COOH","-CO-","c","Carboxylic acid contains -COOH group",1),
    ("Homologous series members differ by?",
     "CH₂","CH₃","C₂H₄","CO₂","a","Each successive member differs by -CH₂- unit",2),
    ("Isomers have same?",
     "Structure","Molecular formula","Physical properties","Boiling point","b","Isomers: same molecular formula, different structures",2),
    ("Benzene molecular formula?",
     "C₆H₁₂","C₆H₆","C₆H₁₄","C₅H₆","b","Benzene: C₆H₆ (aromatic ring)",2),
]

# ── PCB Biology ────────────────────────────────────────────────
QUESTIONS["Cell Division"] = [
    ("DNA replication occurs in which phase?",
     "G1","S phase","G2","M phase","b","DNA replication occurs during S (synthesis) phase",3),
    ("Mitosis produces?",
     "4 haploid cells","2 diploid cells","4 diploid cells","2 haploid cells","b","Mitosis: 2 genetically identical diploid daughter cells",2),
    ("Meiosis reduces chromosome number by?",
     "Half","Double","Quarter","Same","a","Meiosis: diploid → haploid (chromosome number halved)",2),
    ("Spindle fibres attach to chromosome at?",
     "Telomere","Centromere","Chromatid","Nucleosome","b","Spindle fibres attach at centromere during cell division",3),
    ("Crossing over occurs during?",
     "Mitosis","Meiosis I","Meiosis II","Interphase","b","Crossing over (recombination) occurs in prophase I of meiosis",4),
]

QUESTIONS["Photosynthesis"] = [
    ("Light reactions of photosynthesis occur in?",
     "Stroma","Thylakoid membrane","Cytoplasm","Mitochondria","b","Light reactions: thylakoid membrane (grana)",3),
    ("Calvin cycle fixes?",
     "O₂","H₂O","CO₂","N₂","c","Calvin cycle (dark reactions) fixes CO₂ into organic compounds",2),
    ("Photosynthesis overall equation products?",
     "CO₂ + H₂O","Glucose + O₂","ATP + NADPH","ADP + Pi","b","6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂",1),
    ("Chlorophyll absorbs light mainly in?",
     "Green wavelength","Red and blue wavelengths","Yellow wavelength","UV wavelength","b","Chlorophyll absorbs red (~680nm) and blue (~450nm) light",3),
    ("C4 plants avoid photorespiration by?",
     "Closing stomata","Concentrating CO₂ in bundle sheath","Using CAM pathway","Producing more chlorophyll","b","C4 plants: CO₂ concentrated in bundle sheath cells",4),
]

QUESTIONS["Genetics and Mendel"] = [
    ("Mendel's law of segregation states?",
     "Genes assort independently","Alleles separate during gamete formation","Dominant masks recessive","Traits blend","b","Law of segregation: allele pairs separate during meiosis",3),
    ("Genotype Aa × Aa gives phenotypic ratio?",
     "1:2:1","3:1","1:1","2:1","b","Aa × Aa → AA:Aa:aa = 1:2:1; phenotype 3 dominant:1 recessive",3),
    ("Codominance example?",
     "Tall/short peas","ABO blood groups","Eye colour","Skin colour","b","ABO blood group: IA and IB are codominant",4),
    ("Linked genes are located on?",
     "Different chromosomes","Same chromosome","Autosomes only","Sex chromosomes only","b","Linked genes: on same chromosome, tend to be inherited together",4),
    ("Test cross is done with?",
     "Homozygous dominant","Heterozygous","Homozygous recessive","F1 hybrid","c","Test cross: unknown genotype × homozygous recessive",3),
]

QUESTIONS["Molecular Basis of Inheritance"] = [
    ("DNA double helix was proposed by?",
     "Mendel and Morgan","Watson and Crick","Avery and MacLeod","Griffith and Hershey","b","Watson and Crick proposed DNA double helix in 1953",2),
    ("Adenine pairs with?",
     "Cytosine","Guanine","Thymine","Uracil","c","A-T pairing in DNA (2 hydrogen bonds)",2),
    ("Central dogma: DNA → RNA → ?",
     "DNA","Protein","Lipid","Carbohydrate","b","Central dogma: DNA → RNA → Protein",1),
    ("mRNA is translated at?",
     "Nucleus","Ribosome","Mitochondria","Golgi body","b","Translation (mRNA → protein) occurs at ribosomes",2),
    ("Restriction enzymes cut DNA at?",
     "Random sites","Specific palindromic sequences","Only at ends","AT-rich regions","b","Restriction enzymes recognize and cut specific palindromic sequences",4),
]

# ── Commerce ───────────────────────────────────────────────────
QUESTIONS["Partnership Accounts"] = [
    ("In absence of partnership deed, profit sharing ratio is?",
     "Capital ratio","Equal","Time ratio","Arbitrary","b","Without deed: profits shared equally among partners",3),
    ("Goodwill in partnership is valued when?",
     "New partner admitted","Partner retires","Partner dies","All of these","d","Goodwill valued on admission, retirement, or death of partner",3),
    ("Sacrificing ratio = ?",
     "New ratio - Old ratio","Old ratio - New ratio","Old ratio + New ratio","New ratio / Old ratio","b","Sacrificing ratio = Old ratio - New ratio",4),
    ("Revaluation account is a?",
     "Real account","Personal account","Nominal account","None","c","Revaluation account is a nominal account (gains/losses)",3),
    ("Capital account under fixed capital method shows?",
     "All transactions","Only capital changes","Drawings only","Interest only","b","Fixed capital: only capital contributions/withdrawals",3),
]

QUESTIONS["Financial Statements"] = [
    ("Balance sheet shows financial position at?",
     "Over a period","A specific date","Beginning of year","End of quarter","b","Balance sheet: snapshot of financial position on a specific date",2),
    ("Gross profit = ?",
     "Net sales - All expenses","Net sales - Cost of goods sold","Revenue - Tax","Sales - Wages","b","Gross profit = Net sales - Cost of goods sold",2),
    ("Depreciation is charged to?",
     "Balance sheet","Profit & Loss account","Trading account","Capital account","b","Depreciation is an expense → P&L account",2),
    ("Current ratio = ?",
     "Current assets / Current liabilities","Current liabilities / Current assets","Total assets / Total liabilities","Net profit / Sales","a","Current ratio = Current assets / Current liabilities",2),
    ("Closing stock appears in?",
     "Trading account only","Balance sheet only","Both trading account and balance sheet","P&L account","c","Closing stock: credit side of trading account + current asset in balance sheet",4),
]

QUESTIONS["National Income"] = [
    ("GDP stands for?",
     "Gross Domestic Product","General Domestic Production","Gross Demand Product","Government Domestic Policy","a","GDP = Gross Domestic Product",1),
    ("GDP - Depreciation = ?",
     "GNP","NDP","NNP","GNI","b","NDP = GDP - Depreciation (Net Domestic Product)",3),
    ("Transfer payments are?",
     "Included in GDP","Excluded from GDP","Part of investment","Part of exports","b","Transfer payments (pensions, subsidies) not included in GDP",3),
    ("Multiplier effect: if MPC = 0.8, multiplier = ?",
     "0.8","5","1.25","4","b","Multiplier = 1/(1-MPC) = 1/0.2 = 5",4),
    ("Inflation is measured by?",
     "GDP","CPI","GNP","HDI","b","Consumer Price Index (CPI) measures inflation",2),
]

# ── University / CS ────────────────────────────────────────────
QUESTIONS["Dynamic Programming"] = [
    ("Dynamic programming is based on?",
     "Greedy choice","Optimal substructure and overlapping subproblems","Divide and conquer only","Backtracking","b","DP: optimal substructure + overlapping subproblems",3),
    ("Fibonacci using DP has time complexity?",
     "O(2ⁿ)","O(n)","O(n²)","O(log n)","b","DP Fibonacci: O(n) vs O(2ⁿ) naive recursion",3),
    ("Memoization is?",
     "Bottom-up DP","Top-down DP with caching","Greedy approach","Divide and conquer","b","Memoization = top-down DP storing computed results",3),
    ("Longest Common Subsequence of 'ABCD' and 'ACBD'?",
     "2","3","4","1","b","LCS('ABCD','ACBD') = 'ABD' or 'ACD' = length 3",4),
    ("0/1 Knapsack DP table size for n items, capacity W?",
     "n×n","(n+1)×(W+1)","n×W","2ⁿ","b","Knapsack DP: (n+1)×(W+1) table",4),
]

QUESTIONS["Graph Algorithms"] = [
    ("BFS uses which data structure?",
     "Stack","Queue","Priority queue","Heap","b","BFS uses a Queue (FIFO)",2),
    ("Dijkstra's algorithm finds?",
     "Minimum spanning tree","Shortest path from source","All pairs shortest path","Topological order","b","Dijkstra: single-source shortest path (non-negative weights)",3),
    ("Bellman-Ford handles?",
     "Only positive weights","Negative weights","Only unweighted graphs","Only DAGs","b","Bellman-Ford works with negative edge weights",4),
    ("DFS time complexity for graph with V vertices, E edges?",
     "O(V)","O(E)","O(V+E)","O(VE)","c","DFS: O(V+E) — visits each vertex and edge once",3),
    ("Topological sort applies to?",
     "Undirected graphs","Directed Acyclic Graphs (DAG)","Weighted graphs","Complete graphs","b","Topological sort only valid for DAGs",3),
]

QUESTIONS["SQL Basics"] = [
    ("SELECT * FROM table retrieves?",
     "First row","Last row","All rows and columns","Only column names","c","SELECT * returns all rows and all columns",1),
    ("WHERE clause is used to?",
     "Sort results","Filter rows","Group rows","Join tables","b","WHERE filters rows based on condition",1),
    ("JOIN combines rows from?",
     "One table","Two or more tables","Subqueries only","Views only","b","JOIN combines rows from multiple tables based on related columns",2),
    ("GROUP BY is used with?",
     "WHERE","ORDER BY","Aggregate functions","DISTINCT","c","GROUP BY used with aggregate functions (COUNT, SUM, AVG, etc.)",2),
    ("PRIMARY KEY constraint ensures?",
     "Unique values only","Non-null values only","Unique and non-null values","Foreign key reference","c","PRIMARY KEY = UNIQUE + NOT NULL",2),
]

QUESTIONS["Trees"] = [
    ("Height of a balanced binary tree with n nodes?",
     "O(n)","O(log n)","O(n²)","O(1)","b","Balanced BST height = O(log n)",3),
    ("Inorder traversal of BST gives?",
     "Random order","Sorted ascending order","Sorted descending order","Level order","b","BST inorder traversal: left-root-right = sorted ascending",3),
    ("Complete binary tree: all levels filled except?",
     "Root","Last level (filled left to right)","First level","Middle level","b","Complete binary tree: last level filled from left",3),
    ("Number of edges in a tree with n nodes?",
     "n","n+1","n-1","2n","c","Tree with n nodes has exactly n-1 edges",2),
    ("AVL tree maintains balance by ensuring height difference of subtrees ≤ ?",
     "0","1","2","3","b","AVL tree: |height(left) - height(right)| ≤ 1",4),
]

QUESTIONS["Process Management"] = [
    ("PCB stands for?",
     "Program Control Block","Process Control Block","Processor Cache Block","Program Cache Buffer","b","PCB = Process Control Block (stores process state)",2),
    ("Context switch involves?",
     "Creating new process","Saving and restoring process state","Terminating process","Allocating memory","b","Context switch: save current process state, restore next process state",3),
    ("Zombie process is?",
     "Running process","Process waiting for I/O","Terminated process whose parent hasn't read exit status","Blocked process","c","Zombie: process finished but parent hasn't called wait()",4),
    ("Fork() system call creates?",
     "Thread","Child process","New file","Socket","b","fork() creates a child process (copy of parent)",3),
    ("IPC stands for?",
     "Inter-Process Communication","Internal Process Control","Input Process Cache","Interrupt Process Call","a","IPC = Inter-Process Communication",1),
]

# ── More topics across all streams ─────────────────────────────
QUESTIONS["Gravitation"] = [
    ("Universal law of gravitation: F = ?",
     "Gm₁m₂/r","Gm₁m₂/r²","Gm₁m₂r²","Gm₁/m₂r²","b","F = Gm₁m₂/r² (Newton's law of gravitation)",2),
    ("Escape velocity from Earth's surface?",
     "7.9 km/s","11.2 km/s","3 km/s","25 km/s","b","Escape velocity from Earth ≈ 11.2 km/s",3),
    ("Geostationary satellite period?",
     "12 hours","24 hours","1 hour","7 days","b","Geostationary orbit: 24-hour period (matches Earth's rotation)",2),
    ("Gravitational potential energy is?",
     "Always positive","Always negative","Zero at surface","Depends on mass only","b","GPE = -GMm/r (negative, zero at infinity)",4),
    ("Weight of object at centre of Earth?",
     "Maximum","Same as surface","Zero","Half of surface","c","At Earth's centre, g=0, so weight = mg = 0",3),
]

QUESTIONS["Waves"] = [
    ("Speed of sound in air at 0°C?",
     "300 m/s","332 m/s","343 m/s","400 m/s","b","Speed of sound in air at 0°C ≈ 332 m/s",3),
    ("Doppler effect: source moving towards observer, frequency?",
     "Decreases","Increases","Stays same","Becomes zero","b","Source approaching: observed frequency increases",3),
    ("Standing waves form due to?",
     "Single wave","Superposition of two waves travelling in opposite directions","Reflection only","Refraction","b","Standing waves: superposition of incident and reflected waves",4),
    ("Wavelength × frequency = ?",
     "Amplitude","Wave speed","Period","Energy","b","v = fλ (wave speed = frequency × wavelength)",2),
    ("Resonance occurs when driving frequency equals?",
     "Zero","Natural frequency","Double natural frequency","Half natural frequency","b","Resonance: driving frequency = natural frequency of system",3),
]

QUESTIONS["Oscillations"] = [
    ("Time period of simple pendulum depends on?",
     "Mass of bob","Length and g","Amplitude","All of these","b","T = 2π√(L/g); depends only on length and gravity",3),
    ("In SHM, acceleration is proportional to?",
     "Velocity","Displacement (opposite direction)","Time","Amplitude","b","SHM: a = -ω²x (proportional to displacement, opposite direction)",3),
    ("At mean position in SHM, KE is?",
     "Zero","Minimum","Maximum","Equal to PE","c","At mean position: velocity maximum → KE maximum",3),
    ("Angular frequency ω = ?",
     "2πT","2π/T","T/2π","1/T","b","ω = 2π/T = 2πf",2),
    ("Damped oscillation: amplitude?",
     "Increases","Decreases","Stays constant","Oscillates","b","Damped oscillation: amplitude decreases due to energy loss",2),
]

QUESTIONS["Semiconductors"] = [
    ("Intrinsic semiconductor at absolute zero behaves as?",
     "Conductor","Insulator","Semiconductor","Superconductor","b","At 0K, no free electrons → behaves as insulator",3),
    ("p-type semiconductor is formed by doping with?",
     "Pentavalent impurity","Trivalent impurity","Divalent impurity","Hexavalent impurity","b","p-type: trivalent dopant (e.g., Boron) creates holes",3),
    ("In forward biased p-n junction, current?",
     "Does not flow","Flows easily","Flows with high resistance","Depends on temperature","b","Forward bias: low resistance, current flows easily",2),
    ("Zener diode is used for?",
     "Amplification","Voltage regulation","Rectification","Oscillation","b","Zener diode: voltage regulation (works in reverse breakdown)",3),
    ("LED emits light when?",
     "Reverse biased","Forward biased","No bias","At breakdown","b","LED: forward biased p-n junction emits photons",2),
]

QUESTIONS["Hydrocarbons"] = [
    ("Alkanes have general formula?",
     "CₙH₂ₙ","CₙH₂ₙ₊₂","CₙH₂ₙ₋₂","CₙHₙ","b","Alkanes (saturated): CₙH₂ₙ₊₂",2),
    ("Benzene undergoes which type of reaction preferentially?",
     "Addition","Substitution","Elimination","Polymerization","b","Benzene: electrophilic substitution (aromatic stability preserved)",4),
    ("Methane + Cl₂ in presence of UV light gives?",
     "Methanol","Chloromethane","Methanoic acid","Ethane","b","CH₄ + Cl₂ → CH₃Cl + HCl (free radical substitution)",3),
    ("Ethylene (ethene) has which type of bond?",
     "Single bond only","Triple bond","Double bond","Ionic bond","c","Ethene CH₂=CH₂ has a C=C double bond",2),
    ("Acetylene (ethyne) hybridization?",
     "sp³","sp²","sp","sp³d","c","Ethyne HC≡CH: sp hybridization (triple bond)",3),
]

QUESTIONS["Aldehydes and Ketones"] = [
    ("Aldehyde functional group?",
     "-OH","-COOH","-CHO","-CO-","c","Aldehyde: -CHO (carbonyl at end of chain)",1),
    ("Ketone functional group?",
     "-CHO","-CO- (between carbons)","-COOH","-OH","b","Ketone: -CO- (carbonyl between two carbon groups)",1),
    ("Tollens' reagent test is positive for?",
     "Ketones","Aldehydes","Alcohols","Carboxylic acids","b","Tollens' test (silver mirror): positive for aldehydes only",3),
    ("Fehling's solution is reduced by?",
     "Ketones","Aromatic aldehydes","Aliphatic aldehydes","Alcohols","c","Fehling's: reduced by aliphatic aldehydes (not ketones or aromatic)",4),
    ("Acetone (propanone) formula?",
     "CH₃CHO","CH₃COCH₃","HCHO","C₂H₅OH","b","Acetone = propanone = CH₃COCH₃",2),
]

QUESTIONS["Sorting Algorithms"] = [
    ("Quicksort average time complexity?",
     "O(n²)","O(n log n)","O(n)","O(log n)","b","Quicksort average: O(n log n)",3),
    ("Merge sort time complexity (all cases)?",
     "O(n²)","O(n log n)","O(n)","O(log n)","b","Merge sort: always O(n log n)",3),
    ("Bubble sort best case (already sorted)?",
     "O(n²)","O(n log n)","O(n)","O(1)","c","Bubble sort best case (with optimization): O(n)",3),
    ("Which sort is stable?",
     "Quicksort","Heapsort","Merge sort","Selection sort","c","Merge sort is stable (preserves relative order of equal elements)",3),
    ("Insertion sort is efficient for?",
     "Large random arrays","Nearly sorted arrays","Reverse sorted arrays","All cases","b","Insertion sort: O(n) for nearly sorted data",3),
]

QUESTIONS["Recursion and Backtracking"] = [
    ("Base case in recursion is?",
     "The recursive call","The condition that stops recursion","The first call","The return value","b","Base case: condition that terminates recursion",2),
    ("N-Queens problem uses?",
     "Dynamic programming","Greedy","Backtracking","BFS","c","N-Queens: backtracking to explore and prune solutions",4),
    ("Factorial of n using recursion: f(n) = ?",
     "n + f(n-1)","n × f(n-1)","n - f(n-1)","f(n-1) / n","b","f(n) = n × f(n-1), base case f(0) = 1",2),
    ("Stack overflow in recursion occurs due to?",
     "Too many variables","Missing base case or too deep recursion","Heap overflow","Syntax error","b","Stack overflow: call stack exhausted (missing/wrong base case)",3),
    ("Maze solving is typically solved using?",
     "Greedy","DP","Backtracking","Sorting","c","Maze solving: backtracking explores paths and backtracks on dead ends",3),
]

QUESTIONS["Normalization"] = [
    ("1NF requires?",
     "No partial dependencies","Atomic values in each cell","No transitive dependencies","BCNF","b","1NF: all attributes must have atomic (indivisible) values",3),
    ("2NF requires 1NF and?",
     "No transitive dependencies","No partial dependencies on primary key","BCNF","4NF","b","2NF: 1NF + no partial dependencies on composite primary key",3),
    ("3NF requires 2NF and?",
     "No partial dependencies","No transitive dependencies","Atomic values","No multi-valued dependencies","b","3NF: 2NF + no transitive dependencies",3),
    ("BCNF is stricter than?",
     "1NF","2NF","3NF","4NF","c","BCNF is a stronger version of 3NF",4),
    ("Functional dependency A → B means?",
     "B determines A","A determines B","A and B are independent","A equals B","b","A → B: knowing A uniquely determines B",2),
]

QUESTIONS["CPU Scheduling"] = [
    ("FCFS scheduling: process that arrives first?",
     "Gets least CPU","Gets most CPU","Gets CPU first","Gets CPU last","c","FCFS: First Come First Served — arrival order determines execution",1),
    ("Round Robin scheduling uses?",
     "Priority","Time quantum","Burst time","Arrival time","b","Round Robin: each process gets a fixed time quantum",2),
    ("Shortest Job First (SJF) minimizes?",
     "Waiting time","Turnaround time","Average waiting time","Response time","c","SJF minimizes average waiting time",3),
    ("Preemptive scheduling allows?",
     "Process to run until completion","OS to interrupt running process","Only I/O bound processes","Batch processing only","b","Preemptive: OS can interrupt and switch processes",3),
    ("Convoy effect occurs in?",
     "Round Robin","SJF","FCFS","Priority scheduling","c","Convoy effect: short processes wait behind long process in FCFS",4),
]

QUESTIONS["Memory Management"] = [
    ("Paging eliminates?",
     "Internal fragmentation","External fragmentation","Both","Neither","b","Paging eliminates external fragmentation",4),
    ("Page fault occurs when?",
     "Page is in memory","Page is not in memory","TLB hit","Cache hit","b","Page fault: required page not in physical memory",3),
    ("TLB stands for?",
     "Translation Lookaside Buffer","Table Lookup Block","Transfer Level Buffer","Thread Load Balancer","a","TLB = Translation Lookaside Buffer (cache for page table)",2),
    ("Segmentation provides?",
     "Fixed size memory blocks","Variable size logical units","No protection","Contiguous allocation","b","Segmentation: variable-size logical segments (code, data, stack)",3),
    ("LRU page replacement replaces?",
     "Most recently used page","Least recently used page","First loaded page","Random page","b","LRU: evicts the page that was least recently used",3),
]

QUESTIONS["Network Layer IP"] = [
    ("IP address version 4 has how many bits?",
     "16","32","64","128","b","IPv4: 32-bit address",1),
    ("Subnet mask 255.255.255.0 means?",
     "8 host bits","24 host bits","16 host bits","32 host bits","b","255.255.255.0 = /24: 24 network bits, 8 host bits",3),
    ("Default gateway is?",
     "DNS server","Router connecting to other networks","Switch","Firewall","b","Default gateway: router that forwards packets to other networks",2),
    ("ICMP is used for?",
     "File transfer","Error reporting and diagnostics","Email","Web browsing","b","ICMP: Internet Control Message Protocol (ping, traceroute)",2),
    ("NAT stands for?",
     "Network Address Translation","Node Access Table","Network Allocation Table","None","a","NAT = Network Address Translation",1),
]

# ── Arts stream ────────────────────────────────────────────────
QUESTIONS["Mahatma Gandhi and Nationalism"] = [
    ("Gandhi's first major satyagraha in India was at?",
     "Dandi","Champaran","Bardoli","Kheda","b","Champaran Satyagraha (1917) — against indigo planters",3),
    ("Non-Cooperation Movement was launched in?",
     "1915","1920","1930","1942","b","Non-Cooperation Movement launched in 1920",2),
    ("Salt March (Dandi March) was in?",
     "1920","1930","1942","1947","b","Dandi March: March 1930 to protest salt tax",2),
    ("Quit India Movement was launched in?",
     "1940","1942","1944","1945","b","Quit India Movement: August 1942",2),
    ("Gandhi's concept of Swaraj meant?",
     "Military independence","Self-rule and self-reliance","Economic growth","Political power","b","Swaraj: self-rule, self-reliance, moral independence",3),
]

QUESTIONS["Demand"] = [
    ("Law of demand states: as price increases, demand?",
     "Increases","Decreases","Stays same","Doubles","b","Law of demand: inverse relationship between price and quantity demanded",1),
    ("Inferior goods have income elasticity?",
     "Positive","Zero","Negative","Greater than 1","c","Inferior goods: demand falls as income rises → negative income elasticity",3),
    ("Giffen goods violate?",
     "Law of supply","Law of demand","Law of diminishing returns","Engel's law","b","Giffen goods: demand increases as price rises (exception to law of demand)",4),
    ("Substitute goods: if price of tea rises, demand for coffee?",
     "Falls","Rises","Stays same","Becomes zero","b","Substitutes: rise in price of one increases demand for other",2),
    ("Complementary goods: if price of cars rises, demand for petrol?",
     "Rises","Falls","Stays same","Doubles","b","Complements: rise in price of one reduces demand for other",2),
]

QUESTIONS["Human Memory"] = [
    ("Short-term memory capacity is approximately?",
     "3±1 items","7±2 items","15±5 items","Unlimited","b","Miller's Law: STM capacity ≈ 7±2 chunks",3),
    ("Encoding, storage, and retrieval are stages of?",
     "Perception","Memory","Learning","Attention","b","Memory process: encoding → storage → retrieval",2),
    ("Forgetting curve was proposed by?",
     "Freud","Ebbinghaus","Pavlov","Skinner","b","Ebbinghaus forgetting curve: rapid initial forgetting then plateau",3),
    ("Procedural memory stores?",
     "Facts and events","Skills and habits","Emotional memories","Semantic knowledge","b","Procedural memory: how to do things (skills, habits)",3),
    ("Retrieval failure is caused by?",
     "Decay","Interference","Absence of retrieval cues","Repression","c","Retrieval failure: lack of appropriate cues to access stored memory",4),
]


# ── Seeding logic ──────────────────────────────────────────────

def seed_all():
    db.create_tables()

    with db.get_db() as conn:
        all_topics = conn.execute(
            "SELECT id, name FROM topics"
        ).fetchall()

    seeded = 0
    skipped = 0

    for topic_row in all_topics:
        topic_id   = topic_row["id"]
        topic_name = topic_row["name"]

        if topic_name not in QUESTIONS:
            skipped += 1
            continue

        # Check if questions already exist
        with db.get_db() as conn:
            existing = conn.execute(
                "SELECT COUNT(*) as cnt FROM questions WHERE topic_id = ?",
                (topic_id,)
            ).fetchone()["cnt"]

        if existing >= 3:
            print(f"  SKIP  {topic_name} (already has {existing} questions)")
            skipped += 1
            continue

        for (question, opt_a, opt_b, opt_c, opt_d,
             answer, explanation, difficulty) in QUESTIONS[topic_name]:
            db.add_question(
                topic_id    = topic_id,
                question    = question,
                option_a    = opt_a,
                option_b    = opt_b,
                option_c    = opt_c,
                option_d    = opt_d,
                answer      = answer,
                explanation = explanation,
                difficulty  = difficulty,
                source      = "seed"
            )

        print(f"  SEEDED {topic_name} ({len(QUESTIONS[topic_name])} questions)")
        seeded += 1

    print(f"\nDone. Seeded: {seeded} topics | Skipped: {skipped} topics")
    print(f"Topics with questions in bank: {len(QUESTIONS)}")


if __name__ == "__main__":
    print("Seeding questions for all topics...\n")
    seed_all()
