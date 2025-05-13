# Built on the original R implementation code available at:
# https://doi.org/10.5281/zenodo.4606757
# Reference:
# van Hulzen, G., Martin, N., & Depaire, B. (2021). Looking Beyond Activity
# Labels: Mining Context-Aware Resource Profiles Using Activity Instance
# Archetypes. In A. Polyvyanyy, M. T. Wynn, A. Van Looy, & M. Reichert (Eds.),
# Business Process Management Forum - BPM Forum 2021, Rome, Italy, September
# 06-10, 2021, Proceedings (pp. 230–245). Springer.

require(dplyr)
require(lubridate)
require(stringr)
require(fastDummies)
require(flexmix)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 2) {
    fn <- args[1]
    k <- as.integer(args[2])
} else {
    stop("Need to specify two arguments `fn` (filename) and `k` (number of components)")
}

print(fn)
print(k)

# Read event log
sepsis <- read.csv(
    file = fn,
    header = TRUE, 
    encoding = "UTF-8", 
    fileEncoding = "UTF-8-BOM", 
    stringsAsFactors = TRUE
)

# Preprocess data
# load and transform columns
sepsis <- sepsis %>%
    select(
        "case.DiagnosticArtAstrup",
        "case.DiagnosticBlood",
        "case.DiagnosticECG",
        "case.DiagnosticIC",
        "case.DiagnosticLacticAcid",
        "case.DiagnosticLiquor",
        "case.DiagnosticOther",
        "case.DiagnosticSputum",
        "case.DiagnosticUrinaryCulture",
        "case.DiagnosticUrinarySediment",
        "case.DiagnosticXthorax",
        "case.concept.name",
        "case.returning",
        "concept.name",
        "org.resource",
        "time.timestamp"
    ) %>%
    rename(
        CaseID = "case.concept.name",
        Activity = "concept.name",
        CompleteTimestamp = "time.timestamp",
        Resource = "org.resource",
        CaseDiagnosticArtAstrup = "case.DiagnosticArtAstrup",
        CaseDiagnosticBlood = "case.DiagnosticBlood",
        CaseDiagnosticECG = "case.DiagnosticECG",
        CaseDiagnosticIC = "case.DiagnosticIC",
        CaseDiagnosticLacticAcid = "case.DiagnosticLacticAcid",
        CaseDiagnosticLiquor = "case.DiagnosticLiquor",
        CaseDiagnosticOther = "case.DiagnosticOther",
        CaseDiagnosticSputum = "case.DiagnosticSputum",
        CaseDiagnosticUrinaryCulture = "case.DiagnosticUrinaryCulture",
        CaseDiagnosticUrinarySediment = "case.DiagnosticUrinarySediment",
        CaseDiagnosticXthorax = "case.DiagnosticXthorax",
        CaseReturning = "case.returning"
    ) %>%
    mutate(
        CaseDiagnosticArtAstrup = ifelse(CaseDiagnosticArtAstrup == "True", 1, 0),
        CaseDiagnosticBlood = ifelse(CaseDiagnosticBlood == "True", 1, 0),
        CaseDiagnosticECG = ifelse(CaseDiagnosticECG == "True", 1, 0),
        CaseDiagnosticIC = ifelse(CaseDiagnosticIC == "True", 1, 0),
        CaseDiagnosticLacticAcid = ifelse(CaseDiagnosticLacticAcid == "True", 1, 0),
        CaseDiagnosticLiquor = ifelse(CaseDiagnosticLiquor == "True", 1, 0),
        CaseDiagnosticOther = ifelse(CaseDiagnosticOther == "True", 1, 0),
        CaseDiagnosticSputum = ifelse(CaseDiagnosticSputum == "True", 1, 0),
        CaseDiagnosticUrinaryCulture = ifelse(CaseDiagnosticUrinaryCulture == "True", 1, 0),
        CaseDiagnosticUrinarySediment = ifelse(CaseDiagnosticUrinarySediment == "True", 1, 0),
        CaseDiagnosticXthorax = ifelse(CaseDiagnosticXthorax == "True", 1, 0),
        CaseReturning = ifelse(CaseReturning == "True", 1, 0)
    ) %>%
    mutate(
        CaseID = as.factor(CaseID),
        CompleteTimestamp = ymd_hms(CompleteTimestamp),
        Resource = as.factor(Resource),
        Activity = as.factor(Activity),
        Month = as.factor(month(CompleteTimestamp, label = FALSE)),
        Weekday = as.factor(wday(CompleteTimestamp, label = FALSE, week_start = 1))
    )
sepsis <- as.data.frame(sepsis)

# Run clustering with manual loop to store all models
modelBIC <- list()
niter <- 20
for (i in 1:niter) {
    cat(paste0("=== Iter ", i, " ===\n"))
    model <- tryCatch({stepFlexmix(
        formula = . ~ 1,
        data = sepsis,
        k = k,
        nrep = 5,
        model = list(
            FLXMRmultinom(Resource ~ .),

            FLXMCmvbinary(CaseDiagnosticArtAstrup ~ .),
            FLXMCmvbinary(CaseDiagnosticBlood ~ .),
            FLXMCmvbinary(CaseDiagnosticECG ~ .),
            FLXMCmvbinary(CaseDiagnosticIC ~ .),
            FLXMCmvbinary(CaseDiagnosticLacticAcid ~ .),
            FLXMCmvbinary(CaseDiagnosticLiquor ~ .),
            FLXMCmvbinary(CaseDiagnosticOther ~ .),
            FLXMCmvbinary(CaseDiagnosticSputum ~ .),
            FLXMCmvbinary(CaseDiagnosticUrinaryCulture ~ .),
            FLXMCmvbinary(CaseDiagnosticUrinarySediment ~ .),
            FLXMCmvbinary(CaseDiagnosticXthorax ~ .),
            FLXMCmvbinary(CaseReturning ~ .),

            FLXMRmultinom(Activity ~ .),

            FLXMRmultinom(Month ~ .),
            FLXMRmultinom(Weekday ~ .)
        ),
        control = list(
            verbose = 1,
            tolerance = 1e-06,
            iter.max = 500
        )
    )}, error = function(e) {
        return(NULL)
    })
    if (!is.null(model) && !any(is.na(logLik(model)))) {
        newCol <- paste0("ClusterRep", "_", i)
        sepsis[[newCol]] <- clusters(model)
        val <- paste0("BICRep", "_", i)
        modelBIC[[val]] <- BIC(model)
    } else {
        print("Failed to find a solution in this iteration. Pass.")
    }
}

# Export
fnOut <- paste0(fn, ".", "k_", k)
sepsis %>% saveRDS(paste0(fnOut, ".RDS"))
write.csv(sepsis, paste0(fnOut, ".csv"))

print("Finished. Clustering results are exported to RDS and CSV.")

print("BIC values:")
cat(unlist(modelBIC), sep = ",")
cat("\n")

print(paste0("Mean BIC value: ", mean(unlist(modelBIC))))
