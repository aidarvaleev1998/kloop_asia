if [ -z ${LASER+x} ] ; then
  echo "Please set the environment variable 'LASER'"
  exit
fi

# general config
data="."
edir=${data}/embed	# normalized texts and embeddings
lsrc="uz"
ltrg="ru"

# encoder
model_dir="${LASER}/models"
encoder="${model_dir}/bilstm.93langs.2018-12-26.pt"
bpe_codes="${model_dir}/93langs.fcodes"

Embed () {
  ll=$2
  txt="$1.${ll}"
  enc="$1.enc.${ll}"
  if [ ! -s ${enc} ] ; then
    cat ${txt} | python3 ${LASER}/source/embed.py \
      --encoder ${encoder} \
      --token-lang ${ll} \
      --bpe-codes ${bpe_codes} \
      --output ${enc} \
      --verbose
  fi
}

Mine () {
  bn=$1
  l1=$2
  l2=$3
  th=$4
  cand="${bn}.laser-mine-bitexts.tsv"
  if [ ! -s ${cand} ] ; then
    python3 ${LASER}/source/mine_bitexts.py \
       ${bn}.${l1} ${bn}.${l2} \
       --src-lang ${l1} --trg-lang ${l2} \
       --src-embeddings ${bn}.enc.${l1} --trg-embeddings ${bn}.enc.${l2} \
       --unify --mode mine --retrieval max --margin ratio -k 4  \
       --output ${cand} \
       --verbose --gpu
  fi
}

th=1.1
END=8343
for ((i=0;i<=END;i++)); do
  Embed ${edir}/${i} ${lsrc} ${encoder} ${bpe_codes}
  Embed ${edir}/${i} ${ltrg} ${encoder} ${bpe_codes}
  Mine ${edir}/${i} ${lsrc} ${ltrg} ${th}
done
