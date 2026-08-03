import {
  IconArrowDownCircle,
  IconArrowUpCircle,
  IconSend,
} from "@/components/ui/icons";
import type { TransactionType } from "@/types/models";

export const TXN_TYPE_ICON: Record<TransactionType, typeof IconSend> = {
  DEPOSIT: IconArrowDownCircle,
  WITHDRAW: IconArrowUpCircle,
  TRANSFER: IconSend,
};

export const TXN_TYPE_LABEL: Record<TransactionType, string> = {
  DEPOSIT: "Nạp tiền",
  WITHDRAW: "Rút tiền",
  TRANSFER: "Chuyển tiền",
};
