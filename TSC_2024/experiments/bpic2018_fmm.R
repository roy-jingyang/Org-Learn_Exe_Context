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
bpic2018 <- read.csv(
    file = fn,
    header = TRUE, 
    encoding = "UTF-8", 
    fileEncoding = "UTF-8-BOM", 
    stringsAsFactors = TRUE
)

# Preprocess data
# load and transform columns
bpic2018 <- bpic2018 %>%
    select(
        "case.concept.name",
        "case.department",
        "case.redistribution",
        "case.small.farmer", 
        "case.young.farmer",
        "case.selected_risk",
        "case.selected_manually",
        "case.rejected",
        "case.penalty_AJLP",
        "case.penalty_BGKV",
        "case.penalty_AUVP",
        "case.penalty_BGP",
        "case.penalty_C16",
        "case.penalty_BGK",
        "case.penalty_AVUVP",
        "case.penalty_CC",
        "case.penalty_AVJLP",
        "case.penalty_C9",
        "case.penalty_C4",
        "case.penalty_AVGP",
        "case.penalty_ABP",
        "case.penalty_B6",
        "case.penalty_B4",
        "case.penalty_B5",
        "case.penalty_AVBP",
        "case.penalty_B2",
        "case.penalty_B3",
        "case.penalty_AGP",
        "case.penalty_B16",
        "case.penalty_GP1",
        "case.penalty_B5F",
        "case.penalty_V5",
        "case.penalty_JLP6",
        "case.penalty_JLP7",
        "case.penalty_JLP5",
        "case.penalty_JLP2",
        "case.penalty_JLP3",
        "case.penalty_JLP1",

        "activity",
        "doctype",

        "org.resource",

        "time.timestamp"
    ) %>%
    rename(
        CaseID = "case.concept.name",
        CaseDepartment = "case.department",
        CaseRedistribution = "case.redistribution",
        CaseSmallFarmer = "case.small.farmer",
        CaseYoungFarmer = "case.young.farmer",
        CaseSelectedRisk = "case.selected_risk",
        CaseSelectedManually = "case.selected_manually",
        CaseRejected = "case.rejected",
        CasePenaltyAJLP  = "case.penalty_AJLP",
        CasePenaltyBGKV  = "case.penalty_BGKV",
        CasePenaltyAUVP  = "case.penalty_AUVP",
        CasePenaltyBGP   = "case.penalty_BGP",
        CasePenaltyC16   = "case.penalty_C16",
        CasePenaltyBGK   = "case.penalty_BGK",
        CasePenaltyAVUVP = "case.penalty_AVUVP",
        CasePenaltyCC    = "case.penalty_CC",
        CasePenaltyAVJLP = "case.penalty_AVJLP",
        CasePenaltyC9    = "case.penalty_C9",
        CasePenaltyC4    = "case.penalty_C4",
        CasePenaltyAVGP  = "case.penalty_AVGP",
        CasePenaltyABP   = "case.penalty_ABP",
        CasePenaltyB6    = "case.penalty_B6",
        CasePenaltyB4    = "case.penalty_B4",
        CasePenaltyB5    = "case.penalty_B5",
        CasePenaltyAVBP  = "case.penalty_AVBP",
        CasePenaltyB2    = "case.penalty_B2",
        CasePenaltyB3    = "case.penalty_B3",
        CasePenaltyAGP   = "case.penalty_AGP",
        CasePenaltyB16   = "case.penalty_B16",
        CasePenaltyGP1   = "case.penalty_GP1",
        CasePenaltyB5F   = "case.penalty_B5F",
        CasePenaltyV5    = "case.penalty_V5",
        CasePenaltyJLP6  = "case.penalty_JLP6",
        CasePenaltyJLP7  = "case.penalty_JLP7",
        CasePenaltyJLP5  = "case.penalty_JLP5",
        CasePenaltyJLP2  = "case.penalty_JLP2",
        CasePenaltyJLP3  = "case.penalty_JLP3",
        CasePenaltyJLP1  = "case.penalty_JLP1",

        ActivityShort = "activity",
        DocType = "doctype",
        CompleteTimestamp = "time.timestamp",
        Resource = "org.resource"
    ) %>%
    mutate(
        CaseID = as.factor(CaseID),
        CaseDepartment = as.factor(CaseDepartment),
        CompleteTimestamp = ymd_hms(CompleteTimestamp),
        Resource = as.factor(Resource),
        ActivityShort = as.factor(ActivityShort),
        DocType = as.factor(DocType),
        Month = as.factor(month(CompleteTimestamp, label = FALSE)),
        Weekday = as.factor(wday(CompleteTimestamp, label = FALSE, week_start = 1))
    )
bpic2018 <- as.data.frame(bpic2018)

# Run clustering with manual loop to store all models
modelBIC <- list()
niter <- 20
for (i in 1:niter) {
    cat(paste0("=== Iter ", i, " ===\n"))
    set.seed(i)
    model <- stepFlexmix(
        formula = . ~ 1,
        data = bpic2018,
        k = k,
        nrep = 5,
        model = list(
            FLXMRmultinom(Resource ~ .),

            FLXMRmultinom(CaseDepartment ~ .),
            FLXMCmvbinary(CaseRedistribution ~ .),
            FLXMCmvbinary(CaseSmallFarmer ~ .),
            FLXMCmvbinary(CaseYoungFarmer ~ .),
            FLXMCmvbinary(CaseSelectedRisk ~ .),
            FLXMCmvbinary(CaseSelectedManually ~ .),
            FLXMCmvbinary(CaseRejected ~ .),
            FLXMCmvbinary(CasePenaltyAJLP ~ .),
            FLXMCmvbinary(CasePenaltyBGKV ~ .),
            FLXMCmvbinary(CasePenaltyAUVP ~ .),
            FLXMCmvbinary(CasePenaltyBGP ~ .),
            FLXMCmvbinary(CasePenaltyC16 ~ .),
            FLXMCmvbinary(CasePenaltyBGK ~ .),
            FLXMCmvbinary(CasePenaltyAVUVP ~ .),
            FLXMCmvbinary(CasePenaltyCC ~ .),
            FLXMCmvbinary(CasePenaltyAVJLP ~ .),
            FLXMCmvbinary(CasePenaltyC9 ~ .),
            FLXMCmvbinary(CasePenaltyC4 ~ .),
            FLXMCmvbinary(CasePenaltyAVGP ~ .),
            FLXMCmvbinary(CasePenaltyABP ~ .),
            FLXMCmvbinary(CasePenaltyB6 ~ .),
            FLXMCmvbinary(CasePenaltyB4 ~ .),
            FLXMCmvbinary(CasePenaltyB5 ~ .),
            FLXMCmvbinary(CasePenaltyAVBP ~ .),
            FLXMCmvbinary(CasePenaltyB2 ~ .),
            FLXMCmvbinary(CasePenaltyB3 ~ .),
            FLXMCmvbinary(CasePenaltyAGP ~ .),
            FLXMCmvbinary(CasePenaltyB16 ~ .),
            FLXMCmvbinary(CasePenaltyGP1 ~ .),
            FLXMCmvbinary(CasePenaltyB5F ~ .),
            FLXMCmvbinary(CasePenaltyV5 ~ .),
            FLXMCmvbinary(CasePenaltyJLP6 ~ .),
            FLXMCmvbinary(CasePenaltyJLP7 ~ .),
            FLXMCmvbinary(CasePenaltyJLP5 ~ .),
            FLXMCmvbinary(CasePenaltyJLP2 ~ .),
            FLXMCmvbinary(CasePenaltyJLP3 ~ .),
            FLXMCmvbinary(CasePenaltyJLP1 ~ .),

            FLXMRmultinom(ActivityShort ~ .),
            FLXMRmultinom(DocType ~ .),

            FLXMRmultinom(Month ~ .),
            FLXMRmultinom(Weekday ~ .)
        ),
        control = list(
            verbose = 1,
            tolerance = 1e-06,
            iter.max = 500
        )
    )
    # model = getModel(models, as.character(k))
    newCol <- paste0("ClusterRep", "_", i)
    bpic2018[[newCol]] <- clusters(model)
    val <- paste0("BICRep", "_", i)
    modelBIC[[val]] <- BIC(model)
}

# Export
fnOut <- paste0(fn, ".", "k_", k)
bpic2018 %>% saveRDS(paste0(fnOut, ".RDS"))
write.csv(bpic2018, paste0(fnOut, ".csv"))

print("Finished. Clustering results are exported to RDS and CSV.")

print("BIC values:")
cat(unlist(modelBIC), sep = ",")
cat("\n")

print(paste0("Mean BIC value: ", mean(unlist(modelBIC))))
