# Used bash commands

```bash
head -n 10000000 czeng20-csmono > sample
cut -d$'\t' -f 5,6 sample > sentences
sed -i '/^[[:space:]]*$/d' sentences
```